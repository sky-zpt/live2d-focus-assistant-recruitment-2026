"use strict";

window.FocusLive2D = (() => {
  const MODEL_PATH = "/static/models/shizuku/shizuku.model.json";
  const WIDGET_ID = "focus-live2d-widget";
  const CANVAS_ID = "focus-live2d-canvas";
  const SUPPORTED_STATES = new Set(["idle", "focus", "celebrate", "pause", "abandon"]);

  let stage = null;
  let fallback = null;
  let currentState = "idle";
  let initialized = false;
  let focusPulseTimer = null;
  let feedbackAudio = null;

  const FEEDBACK_SOUNDS = {
    focus: "/static/models/shizuku/snd/tapBody_00.mp3",
    celebrate: "/static/models/shizuku/snd/shake_00.mp3",
    idle: "/static/models/shizuku/snd/pinchIn_00.mp3",
    pause: "/static/models/shizuku/snd/pinchIn_01.mp3",
    abandon: "/static/models/shizuku/snd/flickHead_00.mp3",
  };

  function reportFailure(message) {
    if (stage) {
      stage.hidden = true;
    }
    if (fallback) {
      fallback.hidden = false;
    }
    window.dispatchEvent(new CustomEvent("focus-ui-error", { detail: message }));
  }

  function supportsWebGL() {
    const canvas = document.createElement("canvas");
    return Boolean(canvas.getContext("webgl") || canvas.getContext("experimental-webgl"));
  }

  function modelAssetPaths(manifest) {
    const paths = [manifest.model, manifest.physics, manifest.pose, ...manifest.textures];
    (manifest.expressions || []).forEach((expression) => paths.push(expression.file));
    Object.values(manifest.motions || {}).forEach((motions) => {
      motions.forEach((motion) => {
        paths.push(motion.file);
        if (motion.sound) {
          paths.push(motion.sound);
        }
      });
    });
    return [...new Set(paths.filter(Boolean))];
  }

  async function verifyModelAssets() {
    const manifestResponse = await fetch(MODEL_PATH, { cache: "no-store" });
    if (!manifestResponse.ok) {
      throw new Error("模型配置文件无法读取");
    }
    const manifest = await manifestResponse.json();
    const baseUrl = new URL(MODEL_PATH, window.location.origin).toString();
    const assets = modelAssetPaths(manifest).map((path) => new URL(path, baseUrl).toString());
    const responses = await Promise.all(assets.map((path) => fetch(path, { cache: "no-store" })));
    if (responses.some((response) => !response.ok)) {
      throw new Error("模型资源不完整");
    }
  }

  function placeWidget(widget) {
    stage.append(widget);
    Object.assign(widget.style, {
      position: "absolute",
      inset: "0",
      left: "50%",
      right: "auto",
      transform: "translateX(-50%)",
      width: "100%",
      height: "100%",
      zIndex: "1",
      opacity: "1",
      pointerEvents: "none",
    });
  }

  function playFeedbackSound(state) {
    const soundPath = FEEDBACK_SOUNDS[state];
    if (!soundPath) {
      return;
    }
    if (!feedbackAudio) {
      feedbackAudio = new Audio();
      feedbackAudio.volume = 0.45;
    }
    feedbackAudio.pause();
    feedbackAudio.currentTime = 0;
    feedbackAudio.src = soundPath;
    feedbackAudio.play().catch(() => {
      // 浏览器未授予自动播放权限时，角色动作仍然正常工作。
    });
  }

  function triggerFeedback(area = "body") {
    const canvas = document.getElementById(CANVAS_ID);
    if (!canvas) {
      return;
    }
    const rect = canvas.getBoundingClientRect();
    const y = area === "head" ? 0.34 : 0.72;
    window.dispatchEvent(new MouseEvent("mousedown", {
      bubbles: true,
      clientX: rect.left + rect.width / 2,
      clientY: rect.top + rect.height * y,
    }));
  }

  function startFocusPulses() {
    window.clearInterval(focusPulseTimer);
    focusPulseTimer = window.setInterval(() => {
      if (currentState === "focus") {
        triggerFeedback("body");
        playFeedbackSound("focus");
      }
    }, 120000);
  }

  function applyState() {
    if (!stage) {
      return;
    }
    stage.dataset.live2dState = currentState;

    if (currentState === "focus" || currentState === "celebrate") {
      triggerFeedback("body");
    } else if (currentState === "pause" || currentState === "abandon") {
      triggerFeedback("head");
    }
    playFeedbackSound(currentState);
    if (currentState === "focus") {
      startFocusPulses();
    } else {
      window.clearInterval(focusPulseTimer);
    }
  }

  async function init(container) {
    stage = container;
    fallback = document.getElementById("character-fallback");
    if (!stage || !fallback) {
      return Promise.reject(new Error("角色展示区域不存在"));
    }
    if (initialized) {
      return Promise.resolve();
    }
    if (!window.L2Dwidget) {
      reportFailure("角色运行库未加载，专注记录不会受影响。");
      throw new Error("Live2D 运行库未加载");
    }
    if (!supportsWebGL()) {
      reportFailure("浏览器不支持 Live2D 渲染，专注记录不会受影响。");
      throw new Error("浏览器不支持 WebGL");
    }
    try {
      await verifyModelAssets();
    } catch (_error) {
      reportFailure("角色资源加载失败，专注记录不会受影响。");
      throw new Error("Live2D 模型资源加载失败");
    }

    return new Promise((resolve, reject) => {
      let settled = false;
      const timeoutId = window.setTimeout(() => {
        if (!settled) {
          settled = true;
          reportFailure("角色加载超时，专注记录不会受影响。");
          reject(new Error("Live2D 角色加载超时"));
        }
      }, 8000);

      window.L2Dwidget.on("create-container", (widget) => {
        try {
          placeWidget(widget);
        } catch (_error) {
          if (settled) {
            return;
          }
          settled = true;
          window.clearTimeout(timeoutId);
          reportFailure("角色展示失败，专注记录不会受影响。");
          reject(new Error("Live2D 容器初始化失败"));
        }
      });

      window.L2Dwidget.on("create-canvas", () => {
        if (settled) {
          return;
        }
        settled = true;
        initialized = true;
        window.clearTimeout(timeoutId);
        stage.hidden = false;
        fallback.hidden = true;
        applyState();
        resolve();
      });

      try {
        const mobileViewport = window.innerWidth < 800;
        const displayWidth = mobileViewport
          ? Math.max(260, Math.min(340, window.innerWidth - 32))
          : 520;
        const displayHeight = mobileViewport ? 270 : 560;
        window.L2Dwidget.init({
          model: { jsonPath: MODEL_PATH, scale: 1 },
          display: {
            superSample: 1,
            width: displayWidth,
            height: displayHeight,
            position: "right",
            hOffset: 0,
            vOffset: 0,
          },
          mobile: { show: true, scale: 1, motion: true },
          name: { canvas: CANVAS_ID, div: WIDGET_ID },
          react: { opacity: 1 },
          dialog: { enable: false, hitokoto: false },
        });
      } catch (_error) {
        settled = true;
        window.clearTimeout(timeoutId);
        reportFailure("角色无法启动，专注记录不会受影响。");
        reject(new Error("Live2D 角色启动失败"));
      }
    });
  }

  function setState(state) {
    if (!SUPPORTED_STATES.has(state)) {
      return;
    }
    currentState = state;
    if (initialized) {
      applyState();
    }
  }

  return { init, setState };
})();
