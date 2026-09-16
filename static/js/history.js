"use strict";

(() => {
  const historyList = document.getElementById("history-list");
  const emptyState = document.getElementById("history-empty");

  function formatCompletedAt(timestamp) {
    const date = new Date(timestamp);
    if (Number.isNaN(date.getTime())) {
      return "完成时间未知";
    }
    return date.toLocaleString("zh-CN", {
      month: "numeric",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
  }

  function formatMinutes(seconds) {
    return `${Math.round(Number(seconds) / 60)} 分钟`;
  }

  function createHistoryItem(session) {
    const item = document.createElement("li");
    item.className = "history-item";

    const task = document.createElement("strong");
    task.className = "history-task";
    task.textContent = session.task_text;

    const metadata = document.createElement("span");
    metadata.className = "history-meta";
    metadata.textContent = `${formatCompletedAt(session.finished_at)} · ${formatMinutes(session.duration_seconds)}`;

    item.append(task, metadata);
    return item;
  }

  function renderHistory(sessions) {
    historyList.replaceChildren();
    emptyState.hidden = sessions.length > 0;
    sessions.forEach((session) => historyList.append(createHistoryItem(session)));
  }

  function reportHistoryError() {
    window.dispatchEvent(
      new CustomEvent("focus-ui-error", {
        detail: "完成记录暂时无法加载，请稍后刷新页面重试。",
      }),
    );
  }

  async function loadHistory() {
    try {
      const { sessions } = await window.FocusApi.listCompletedSessions(10);
      renderHistory(sessions);
    } catch (_error) {
      reportHistoryError();
    }
  }

  window.addEventListener("focus-session-completed", loadHistory);
  window.FocusHistory = { loadHistory, renderHistory };
  loadHistory();
})();
