"use strict";

window.FocusTimer = (() => {
  function clampSeconds(value) {
    return Math.max(0, Math.floor(Number(value) || 0));
  }

  function calculateRemainingSeconds(session, now = Date.now()) {
    const storedRemaining = clampSeconds(session.remaining_seconds);
    if (session.status !== "active" || !session.last_started_at) {
      return storedRemaining;
    }

    const startedAt = new Date(session.last_started_at).getTime();
    if (Number.isNaN(startedAt)) {
      return storedRemaining;
    }
    const elapsedSeconds = Math.max(0, Math.floor((now - startedAt) / 1000));
    return Math.max(0, storedRemaining - elapsedSeconds);
  }

  function formatDuration(seconds) {
    const safeSeconds = clampSeconds(seconds);
    const minutes = Math.floor(safeSeconds / 60);
    const remainingSeconds = safeSeconds % 60;
    return `${String(minutes).padStart(2, "0")}:${String(remainingSeconds).padStart(2, "0")}`;
  }

  class Timer {
    constructor({ onTick, onFinished }) {
      this.onTick = onTick;
      this.onFinished = onFinished;
      this.intervalId = null;
      this.session = null;
    }

    start(session) {
      this.stop();
      this.session = session;
      this.tick();
      if (this.getRemainingSeconds() > 0) {
        this.intervalId = window.setInterval(() => this.tick(), 250);
      }
    }

    show(seconds) {
      this.stop();
      this.onTick(clampSeconds(seconds));
    }

    stop() {
      if (this.intervalId !== null) {
        window.clearInterval(this.intervalId);
        this.intervalId = null;
      }
      this.session = null;
    }

    getRemainingSeconds() {
      if (this.session === null) {
        return 0;
      }
      return calculateRemainingSeconds(this.session);
    }

    tick() {
      const remainingSeconds = this.getRemainingSeconds();
      this.onTick(remainingSeconds);
      if (remainingSeconds === 0) {
        this.stop();
        this.onFinished();
      }
    }
  }

  return { Timer, calculateRemainingSeconds, formatDuration };
})();
