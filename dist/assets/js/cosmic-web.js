/** Interactive, dependency-free cosmic-web renderer.
 * It is intentionally isolated from the rest of the UI so it can later be
 * replaced by Three.js/WebGL without rewriting the website.
 */
export class CosmicWeb {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d', { alpha: true });
    this.nodes = [];
    this.pointer = { x: 0, y: 0, active: false };
    this.raf = 0;
    this.last = 0;
    this.reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
    this.resizeObserver = new ResizeObserver(() => this.resize());
    this.resizeObserver.observe(canvas.parentElement);
    this.bind();
    this.resize();
    if (!this.reduceMotion) this.raf = requestAnimationFrame((t) => this.draw(t));
    else this.drawStatic();
  }

  bind() {
    const host = this.canvas.parentElement;
    host.addEventListener('pointermove', (event) => {
      const rect = host.getBoundingClientRect();
      this.pointer.x = event.clientX - rect.left;
      this.pointer.y = event.clientY - rect.top;
      this.pointer.active = true;
    }, { passive: true });
    host.addEventListener('pointerleave', () => { this.pointer.active = false; }, { passive: true });
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) cancelAnimationFrame(this.raf);
      else if (!this.reduceMotion) this.raf = requestAnimationFrame((t) => this.draw(t));
    });
  }

  resize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 1.75);
    this.width = Math.max(1, rect.width);
    this.height = Math.max(1, rect.height);
    this.canvas.width = Math.round(this.width * dpr);
    this.canvas.height = Math.round(this.height * dpr);
    this.canvas.style.width = `${this.width}px`;
    this.canvas.style.height = `${this.height}px`;
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    this.createNodes();
  }

  createNodes() {
    const density = this.width < 700 ? 34 : this.width < 1200 ? 58 : 82;
    this.nodes = Array.from({ length: density }, (_, index) => {
      const focus = index < Math.floor(density * .46);
      const x = focus
        ? this.width * (.48 + Math.random() * .44)
        : Math.random() * this.width;
      const y = focus
        ? this.height * (.12 + Math.random() * .76)
        : Math.random() * this.height;
      return {
        x, y,
        homeX: x,
        homeY: y,
        vx: (Math.random() - .5) * .075,
        vy: (Math.random() - .5) * .075,
        r: Math.random() * 1.45 + .45,
        phase: Math.random() * Math.PI * 2,
        focus
      };
    });
  }

  update(dt) {
    for (const node of this.nodes) {
      node.phase += dt * .00035;
      node.x += node.vx * dt;
      node.y += node.vy * dt;
      node.x += Math.sin(node.phase) * .014 * dt;
      node.y += Math.cos(node.phase * .83) * .009 * dt;

      if (this.pointer.active) {
        const dx = this.pointer.x - node.x;
        const dy = this.pointer.y - node.y;
        const dist2 = dx * dx + dy * dy;
        if (dist2 < 42000 && dist2 > 1) {
          const force = (1 - dist2 / 42000) * .00023 * dt;
          node.x += dx * force;
          node.y += dy * force;
        }
      }
      const margin = 40;
      if (node.x < -margin) node.x = this.width + margin;
      if (node.x > this.width + margin) node.x = -margin;
      if (node.y < -margin) node.y = this.height + margin;
      if (node.y > this.height + margin) node.y = -margin;
    }
  }

  paint(time = 0) {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.width, this.height);

    const glow = ctx.createRadialGradient(this.width * .68, this.height * .43, 0, this.width * .68, this.height * .43, this.width * .42);
    glow.addColorStop(0, 'rgba(106,151,224,.12)');
    glow.addColorStop(.28, 'rgba(67,104,169,.055)');
    glow.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = glow;
    ctx.fillRect(0, 0, this.width, this.height);

    const threshold = Math.min(165, Math.max(112, this.width * .105));
    for (let i = 0; i < this.nodes.length; i++) {
      const a = this.nodes[i];
      for (let j = i + 1; j < this.nodes.length; j++) {
        const b = this.nodes[j];
        const dx = a.x - b.x;
        const dy = a.y - b.y;
        const distance = Math.hypot(dx, dy);
        if (distance < threshold) {
          const alpha = (1 - distance / threshold) * (a.focus && b.focus ? .28 : .12);
          const gradient = ctx.createLinearGradient(a.x, a.y, b.x, b.y);
          gradient.addColorStop(0, `rgba(103,151,229,${alpha})`);
          gradient.addColorStop(.55, `rgba(150,183,236,${alpha * .92})`);
          gradient.addColorStop(1, `rgba(216,189,134,${alpha * .85})`);
          ctx.strokeStyle = gradient;
          ctx.lineWidth = a.focus && b.focus ? .8 : .45;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          const bend = Math.sin((a.phase + b.phase + time * .00008)) * 8;
          ctx.quadraticCurveTo((a.x + b.x) / 2 + bend, (a.y + b.y) / 2 - bend, b.x, b.y);
          ctx.stroke();
        }
      }
    }

    for (const node of this.nodes) {
      const pulse = .72 + Math.sin(node.phase + time * .001) * .28;
      if (node.focus && node.r > 1.2) {
        ctx.fillStyle = `rgba(219,190,131,${.08 * pulse})`;
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.r * 7, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.fillStyle = node.focus
        ? `rgba(235,221,187,${.72 * pulse})`
        : `rgba(154,188,240,${.42 * pulse})`;
      ctx.beginPath();
      ctx.arc(node.x, node.y, node.r, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  draw(time) {
    const dt = Math.min(32, time - this.last || 16);
    this.last = time;
    this.update(dt);
    this.paint(time);
    this.raf = requestAnimationFrame((t) => this.draw(t));
  }

  drawStatic() { this.paint(0); }
  destroy() { cancelAnimationFrame(this.raf); this.resizeObserver.disconnect(); }
}
