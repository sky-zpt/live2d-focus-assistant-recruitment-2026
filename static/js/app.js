"use strict";

(() => {
  function buildCatPattern() {
    const pattern = document.getElementById("cat-pattern");
    if (!pattern) {
      return;
    }
    const catUrl = "/static/assets/cat-transparent.png";
    const spacingX = 205;
    const spacingY = 172;
    const columns = Math.ceil(window.innerWidth / spacingX) + 2;
    const rows = Math.ceil(window.innerHeight / spacingY) + 2;
    const fragment = document.createDocumentFragment();

    for (let row = -1; row < rows; row += 1) {
      for (let column = -1; column < columns; column += 1) {
        const cat = document.createElement("img");
        cat.className = "cat-pattern-item";
        cat.src = catUrl;
        cat.alt = "";
        cat.style.left = `${column * spacingX + (row % 2 ? spacingX / 2 : 0)}px`;
        cat.style.top = `${row * spacingY}px`;
        fragment.append(cat);
      }
    }
    pattern.replaceChildren(fragment);
  }

  buildCatPattern();

  const STATES = {
    IDLE: "idle",
    RUNNING: "running",
    PAUSED: "paused",
    READY_TO_COMPLETE: "ready_to_complete",
    COMPLETED: "completed",
  };
  const DEFAULT_DURATION_SECONDS = 25 * 60;

  const elements = {
    form: document.getElementById("task-form"),
    taskInput: document.getElementById("task-input"),
    durationInput: document.getElementById("duration-input"),
    startButton: document.getElementById("start-button"),
    timerDisplay: document.getElementById("timer-display"),
    pauseButton: document.getElementById("pause-button"),
    resumeButton: document.getElementById("resume-button"),
    completeButton: document.getElementById("complete-button"),
    abandonButton: document.getElementById("abandon-button"),
    status: document.getElementById("assistant-status"),
    error: document.getElementById("error-message"),
  };

  let state = STATES.IDLE;
  let activeSession = null;
  let busy = false;

  const timer = new window.FocusTimer.Timer({
    onTick: (seconds) => {
      elements.timerDisplay.value = window.FocusTimer.formatDuration(seconds);
      elements.timerDisplay.textContent = window.FocusTimer.formatDuration(seconds);
    },
    onFinished: () => {
      if (state === STATES.RUNNING) {
        setPageState(STATES.READY_TO_COMPLETE);
        setStatus("时间到了，确认完成这一件事吧。\n");
      }
    },
  });

  function setPageState(nextState) {
    state = nextState;
    const taskEntryVisible = nextState === STATES.IDLE || nextState === STATES.COMPLETED;
    elements.form.hidden = !taskEntryVisible;
    elements.pauseButton.hidden = nextState !== STATES.RUNNING;
    elements.resumeButton.hidden = nextState !== STATES.PAUSED;
    elements.completeButton.hidden = nextState !== STATES.READY_TO_COMPLETE;
    elements.abandonButton.hidden = ![
      STATES.RUNNING,
      STATES.PAUSED,
      STATES.READY_TO_COMPLETE,
    ].includes(nextState);
    if (window.FocusLive2D) {
      const characterState = nextState === STATES.RUNNING
        ? "focus"
        : nextState === STATES.COMPLETED
          ? "celebrate"
          : nextState === STATES.PAUSED
            ? "pause"
            : "idle";
      window.FocusLive2D.setState(characterState);
    }
  }

  function setStatus(message) {
    elements.status.textContent = message;
  }

  function clearError() {
    elements.error.hidden = true;
    elements.error.textContent = "";
  }

  function showError(error) {
    const message = error instanceof Error ? error.message : "发生未知错误，请重试。";
    elements.error.textContent = message;
    elements.error.hidden = false;
    setStatus("操作暂未完成，请检查提示后重试。\n");
  }

  window.addEventListener("focus-ui-error", (event) => {
    elements.error.textContent = event.detail || "页面功能暂时不可用。";
    elements.error.hidden = false;
  });

  function setBusy(nextBusy) {
    busy = nextBusy;
    [
      elements.startButton,
      elements.pauseButton,
      elements.resumeButton,
      elements.completeButton,
      elements.abandonButton,
    ].forEach((button) => {
      button.disabled = nextBusy;
    });
  }

  async function runAction(action) {
    if (busy) {
      return;
    }
    setBusy(true);
    clearError();
    try {
      await action();
    } catch (error) {
      showError(error);
    } finally {
      setBusy(false);
    }
  }

  function startTimer(session) {
    activeSession = session;
    if (window.FocusTimer.calculateRemainingSeconds(session) === 0) {
      timer.show(0);
      setPageState(STATES.READY_TO_COMPLETE);
      setStatus("时间到了，确认完成这一件事吧。\n");
      return;
    }
    setPageState(STATES.RUNNING);
    timer.start(session);
  }

  async function restoreActiveSession() {
    await runAction(async () => {
      const { session } = await window.FocusApi.getActiveSession();
      if (session === null) {
        timer.show(DEFAULT_DURATION_SECONDS);
        setPageState(STATES.IDLE);
        return;
      }
      activeSession = session;
      if (session.status === STATES.PAUSED) {
        timer.show(session.remaining_seconds);
        setPageState(STATES.PAUSED);
        setStatus(`“${session.task_text}”已暂停，准备好后继续。`);
        return;
      }
      startTimer(session);
      setStatus(`正在专注：“${session.task_text}”`);
    });
  }

  elements.form.addEventListener("submit", (event) => {
    event.preventDefault();
    const taskText = elements.taskInput.value.trim();
    const durationMinutes = Number(elements.durationInput.value);
    if (!taskText) {
      showError(new Error("请输入要完成的任务。"));
      elements.taskInput.focus();
      return;
    }
    if (!Number.isInteger(durationMinutes) || durationMinutes < 1 || durationMinutes > 120) {
      showError(new Error("专注时长必须在 1 到 120 分钟之间。"));
      elements.durationInput.focus();
      return;
    }
    runAction(async () => {
      const { session } = await window.FocusApi.createSession(taskText, durationMinutes);
      elements.taskInput.value = "";
      startTimer(session);
      setStatus(`开始专注：“${session.task_text}”`);
    });
  });

  elements.pauseButton.addEventListener("click", () => {
    runAction(async () => {
      const { session } = await window.FocusApi.pauseSession(activeSession.id);
      activeSession = session;
      timer.show(session.remaining_seconds);
      setPageState(STATES.PAUSED);
      setStatus("已暂停，休息一下也没关系。\n");
    });
  });

  elements.resumeButton.addEventListener("click", () => {
    runAction(async () => {
      const { session } = await window.FocusApi.resumeSession(activeSession.id);
      startTimer(session);
      setStatus(`继续专注：“${session.task_text}”`);
    });
  });

  elements.completeButton.addEventListener("click", () => {
    runAction(async () => {
      const { session } = await window.FocusApi.completeSession(activeSession.id);
      activeSession = null;
      timer.show(DEFAULT_DURATION_SECONDS);
      setPageState(STATES.COMPLETED);
      setStatus(`完成了“${session.task_text}”，做得好！`);
      window.dispatchEvent(new CustomEvent("focus-session-completed", { detail: session }));
    });
  });

  elements.abandonButton.addEventListener("click", () => {
    runAction(async () => {
      await window.FocusApi.abandonSession(activeSession.id);
      activeSession = null;
      timer.show(DEFAULT_DURATION_SECONDS);
      setPageState(STATES.IDLE);
      if (window.FocusLive2D) {
        window.FocusLive2D.setState("abandon");
      }
      setStatus("这次先放下，随时可以重新开始。\n");
    });
  });

  setPageState(STATES.IDLE);
  timer.show(DEFAULT_DURATION_SECONDS);
  restoreActiveSession();
  window.FocusUi = { setStatus, showError };
  if (window.FocusLive2D) {
    window.FocusLive2D.init(document.getElementById("live2d-container")).catch(() => {});
  }
})();
