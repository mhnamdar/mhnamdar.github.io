/** Interactive cosmic-web background for the home hero. */
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
    if (!this.reduceMotion) {
      this.raf = requestAnimationFrame((t) => this.draw(t));
    } else {
      this.drawStatic();
    }
  }

  bind() {
    const host = this.canvas.parentElement;

    host.addEventListener('pointermove', (event) => {
      const rect = host.getBoundingClientRect();
      this.pointer.x = event.clientX - rect.left;
      this.pointer.y = event.clientY - rect.top;
      this.pointer.active = true;
    }, { passive: true });

    host.addEventListener('pointerleave', () => {
      this.pointer.active = false;
    }, { passive: true });

    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        cancelAnimationFrame(this.raf);
      } else if (!this.reduceMotion) {
        this.raf = requestAnimationFrame((t) => this.draw(t));
      }
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
    const density = this.width < 700 ? 52 : this.width < 1200 ? 84 : 116;

    this.nodes = Array.from({ length: density }, (_, index) => {
      const focus = index < Math.floor(density * 0.62);

      const x = focus
        ? this.width * (0.50 + Math.random() * 0.42)
        : Math.random() * this.width;

      const y = focus
        ? this.height * (0.10 + Math.random() * 0.78)
        : Math.random() * this.height;

      return {
        x,
        y,
        homeX: x,
        homeY: y,
        vx: (Math.random() - 0.5) * 0.05,
        vy: (Math.random() - 0.5) * 0.05,
        r: Math.random() * 1.6 + 0.4,
        phase: Math.random() * Math.PI * 2,
        focus
      };
    });
  }

  update(dt) {
    const influenceRadius = 160;

    for (const node of this.nodes) {
      node.phase += dt * 0.00036;

      const homePullX = (node.homeX - node.x) * 0.00042 * dt;
      const homePullY = (node.homeY - node.y) * 0.00042 * dt;

      node.x += node.vx * dt + homePullX;
      node.y += node.vy * dt + homePullY;

      node.x += Math.sin(node.phase) * 0.018 * dt;
      node.y += Math.cos(node.phase * 0.83) * 0.012 * dt;

      if (this.pointer.active) {
        const dx = this.pointer.x - node.x;
        const dy = this.pointer.y - node.y;
        const dist = Math.hypot(dx, dy);

        if (dist < influenceRadius && dist > 1) {
          const falloff = 1 - dist / influenceRadius;

          const radialX = dx / dist;
          const radialY = dy / dist;

          const tangentX = -dy / dist;
          const tangentY = dx / dist;

          node.x += radialX * falloff * 0.42 * dt;
          node.y += radialY * falloff * 0.42 * dt;

          node.x += tangentX * falloff * 0.14 * dt;
          node.y += tangentY * falloff * 0.14 * dt;
        }
      }

      const margin = 50;
      if (node.x < -margin) node.x = this.width + margin;
      if (node.x > this.width + margin) node.x = -margin;
      if (node.y < -margin) node.y = this.height + margin;
      if (node.y > this.height + margin) node.y = -margin;
    }
  }

  paint(time = 0) {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.width, this.height);

    const bgGlow = ctx.createRadialGradient(
      this.width * 0.72,
      this.height * 0.42,
      0,
      this.width * 0.72,
      this.height * 0.42,
      this.width * 0.42
    );
    bgGlow.addColorStop(0, 'rgba(115,155,230,0.16)');
    bgGlow.addColorStop(0.28, 'rgba(82,118,196,0.08)');
    bgGlow.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = bgGlow;
    ctx.fillRect(0, 0, this.width, this.height);

    const nebulaA = ctx.createRadialGradient(
      this.width * 0.66, this.height * 0.33, 0,
      this.width * 0.66, this.height * 0.33, this.width * 0.18
    );
    nebulaA.addColorStop(0, 'rgba(158,123,255,0.10)');
    nebulaA.addColorStop(0.5, 'rgba(86,106,228,0.08)');
    nebulaA.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = nebulaA;
    ctx.fillRect(0, 0, this.width, this.height);

    const nebulaB = ctx.createRadialGradient(
      this.width * 0.56, this.height * 0.62, 0,
      this.width * 0.56, this.height * 0.62, this.width * 0.14
    );
    nebulaB.addColorStop(0, 'rgba(100,180,255,0.08)');
    nebulaB.addColorStop(0.5, 'rgba(58,95,182,0.06)');
    nebulaB.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = nebulaB;
    ctx.fillRect(0, 0, this.width, this.height);

    if (this.pointer.active) {
      const pointerGlow = ctx.createRadialGradient(
        this.pointer.x, this.pointer.y, 0,
        this.pointer.x, this.pointer.y, 130
      );
      pointerGlow.addColorStop(0, 'rgba(244,223,168,0.12)');
      pointerGlow.addColorStop(0.45, 'rgba(121,162,231,0.09)');
      pointerGlow.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = pointerGlow;
      ctx.fillRect(0, 0, this.width, this.height);
    }

    const threshold = Math.min(170, Math.max(110, this.width * 0.11));

    for (let i = 0; i < this.nodes.length; i++) {
      const a = this.nodes[i];
      for (let j = i + 1; j < this.nodes.length; j++) {
        const b = this.nodes[j];
        const dx = a.x - b.x;
        const dy = a.y - b.y;
        const distance = Math.hypot(dx, dy);

        if (distance < threshold) {
          const alpha = (1 - distance / threshold) * (a.focus && b.focus ? 0.30 : 0.11);

          const gradient = ctx.createLinearGradient(a.x, a.y, b.x, b.y);
          gradient.addColorStop(0, `rgba(103,151,229,${alpha})`);
          gradient.addColorStop(0.55, `rgba(150,183,236,${alpha * 0.92})`);
          gradient.addColorStop(1, `rgba(216,189,134,${alpha * 0.82})`);

          ctx.strokeStyle = gradient;
          ctx.lineWidth = a.focus && b.focus ? 0.82 : 0.42;

          ctx.beginPath();
          ctx.moveTo(a.x, a.y);

          const bend = Math.sin(a.phase + b.phase + time * 0.00008) * 9;
          ctx.quadraticCurveTo(
            (a.x + b.x) / 2 + bend,
            (a.y + b.y) / 2 - bend,
            b.x,
            b.y
          );
          ctx.stroke();
        }
      }
    }

    for (const node of this.nodes) {
      const pulse = 0.72 + Math.sin(node.phase + time * 0.001) * 0.28;

      if (node.focus && node.r > 1.25) {
        ctx.fillStyle = `rgba(219,190,131,${0.08 * pulse})`;
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.r * 7, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.fillStyle = node.focus
        ? `rgba(235,221,187,${0.76 * pulse})`
        : `rgba(154,188,240,${0.42 * pulse})`;

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

  drawStatic() {
    this.paint(0);
  }

  destroy() {
    cancelAnimationFrame(this.raf);
    this.resizeObserver.disconnect();
  }
}
