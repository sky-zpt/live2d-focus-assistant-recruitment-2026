"use strict";

window.FocusApi = (() => {
  async function request(path, options = {}) {
    const response = await fetch(path, {
      headers: { Accept: "application/json", ...options.headers },
      ...options,
    });
    const payload = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(payload.error || "请求失败，请稍后再试。", {
        cause: { status: response.status },
      });
    }
    return payload;
  }

  function post(path, body) {
    const options = { method: "POST" };
    if (body !== undefined) {
      options.headers = { "Content-Type": "application/json" };
      options.body = JSON.stringify(body);
    }
    return request(path, options);
  }

  return {
    getActiveSession: () => request("/api/sessions/active"),
    createSession: (taskText, durationMinutes = 25) => post("/api/sessions", {
      task_text: taskText,
      duration_minutes: durationMinutes,
    }),
    pauseSession: (sessionId) => post(`/api/sessions/${sessionId}/pause`),
    resumeSession: (sessionId) => post(`/api/sessions/${sessionId}/resume`),
    completeSession: (sessionId) => post(`/api/sessions/${sessionId}/complete`),
    abandonSession: (sessionId) => post(`/api/sessions/${sessionId}/abandon`),
    listCompletedSessions: (limit = 10) => request(`/api/sessions?limit=${limit}`),
  };
})();
