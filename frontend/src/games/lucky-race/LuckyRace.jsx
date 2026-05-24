function LuckyTrackCanvas({ data, progress }) {
  const canvasRef = useRef(null);
  const logosRef = useRef({});

  useEffect(() => {
    const keys = ["bmw", "audi", "tata", "mercedes", "ferrari", "porsche", "mahindra", "lucky"];

    keys.forEach((key) => {
      const img = new Image();
      img.src = `/car-logos/${key}.png`;
      logosRef.current[key.toUpperCase()] = img;
    });
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const parent = canvas.parentElement;
    const ctx = canvas.getContext("2d");

    let raf = 0;

    function roundRect(ctx, x, y, w, h, r) {
      ctx.beginPath();
      ctx.moveTo(x + r, y);
      ctx.lineTo(x + w - r, y);
      ctx.quadraticCurveTo(x + w, y, x + w, y + r);
      ctx.lineTo(x + w, y + h - r);
      ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
      ctx.lineTo(x + r, y + h);
      ctx.quadraticCurveTo(x, y + h, x, y + h - r);
      ctx.lineTo(x, y + r);
      ctx.quadraticCurveTo(x, y, x + r, y);
      ctx.closePath();
    }

    function drawLogoSlot(ctx, x, y, car, isActive, isWinner, t) {
      const key = String(car.key || "").toUpperCase();
      const logo = logosRef.current[key];

      ctx.save();

      if (isActive || isWinner) {
        const pulse = 1 + Math.sin(t / 120) * 0.08;
        ctx.translate(x, y);
        ctx.scale(pulse, pulse);
        ctx.translate(-x, -y);

        const glow = ctx.createRadialGradient(x, y, 8, x, y, 46);
        glow.addColorStop(0, "rgba(255, 245, 60, 0.95)");
        glow.addColorStop(0.45, "rgba(255, 216, 0, 0.45)");
        glow.addColorStop(1, "rgba(255, 216, 0, 0)");

        ctx.fillStyle = glow;
        ctx.beginPath();
        ctx.arc(x, y, 52, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = "#fff157";
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.arc(x, y, 39, 0, Math.PI * 2);
        ctx.stroke();

        ctx.fillStyle = "#fff157";
        ctx.font = "900 28px Arial";
        ctx.shadowColor = "#fff157";
        ctx.shadowBlur = 14;
        ctx.fillText("★", x + 28, y - 24);
        ctx.shadowBlur = 0;
      }

      const outer = ctx.createLinearGradient(x - 35, y - 35, x + 35, y + 35);
      outer.addColorStop(0, "#6b6d82");
      outer.addColorStop(1, "#171722");

      ctx.fillStyle = outer;
      ctx.beginPath();
      ctx.arc(x, y, 35, 0, Math.PI * 2);
      ctx.fill();

      ctx.strokeStyle = isWinner ? "#ffffff" : isActive ? "#fff157" : "#808295";
      ctx.lineWidth = 4;
      ctx.stroke();

      ctx.fillStyle = "#11121c";
      ctx.beginPath();
      ctx.arc(x, y, 28, 0, Math.PI * 2);
      ctx.fill();

      if (logo && logo.complete && logo.naturalWidth > 0) {
        ctx.drawImage(logo, x - 24, y - 24, 48, 48);
      } else {
        ctx.fillStyle = "#ffffff";
        ctx.font = "900 20px Arial";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(car.icon || key[0] || "?", x, y);
      }

      ctx.restore();
    }

    function draw(t = 0) {
      const rect = parent.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;

      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      canvas.style.width = `${rect.width}px`;
      canvas.style.height = `${rect.height}px`;

      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      const w = rect.width;
      const h = rect.height;

      ctx.clearRect(0, 0, w, h);

      const bg = ctx.createLinearGradient(0, 0, 0, h);
      bg.addColorStop(0, "#1b0d4a");
      bg.addColorStop(0.48, "#13072e");
      bg.addColorStop(1, "#070712");
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, w, h);

      const centerGlow = ctx.createRadialGradient(w / 2, h * 0.54, 20, w / 2, h * 0.54, w * 0.42);
      centerGlow.addColorStop(0, "rgba(112, 67, 255, 0.95)");
      centerGlow.addColorStop(0.45, "rgba(80, 50, 230, 0.38)");
      centerGlow.addColorStop(1, "rgba(80, 50, 230, 0)");
      ctx.fillStyle = centerGlow;
      ctx.fillRect(0, 0, w, h);

      const beamLeft = ctx.createLinearGradient(w * 0.48, h * 0.45, w * 0.05, h * 0.22);
      beamLeft.addColorStop(0, "rgba(100, 100, 255, 0.55)");
      beamLeft.addColorStop(1, "rgba(100, 100, 255, 0)");
      ctx.fillStyle = beamLeft;
      ctx.beginPath();
      ctx.moveTo(w * 0.48, h * 0.38);
      ctx.lineTo(w * 0.05, h * 0.18);
      ctx.lineTo(w * 0.05, h * 0.78);
      ctx.lineTo(w * 0.48, h * 0.62);
      ctx.closePath();
      ctx.fill();

      const beamRight = ctx.createLinearGradient(w * 0.52, h * 0.45, w * 0.95, h * 0.22);
      beamRight.addColorStop(0, "rgba(100, 100, 255, 0.55)");
      beamRight.addColorStop(1, "rgba(100, 100, 255, 0)");
      ctx.fillStyle = beamRight;
      ctx.beginPath();
      ctx.moveTo(w * 0.52, h * 0.38);
      ctx.lineTo(w * 0.95, h * 0.18);
      ctx.lineTo(w * 0.95, h * 0.78);
      ctx.lineTo(w * 0.52, h * 0.62);
      ctx.closePath();
      ctx.fill();

      ctx.strokeStyle = "rgba(210, 220, 255, 0.32)";
      ctx.lineWidth = 3;
      roundRect(ctx, w * 0.03, h * 0.08, w * 0.94, h * 0.84, 92);
      ctx.stroke();

      ctx.strokeStyle = "rgba(140, 155, 210, 0.25)";
      ctx.lineWidth = 2;
      roundRect(ctx, w * 0.065, h * 0.23, w * 0.87, h * 0.58, 70);
      ctx.stroke();

      // center machine
      const mx = w / 2 - 170;
      const my = h * 0.29;
      const mw = 340;
      const mh = 116;

      ctx.fillStyle = "rgba(5, 7, 18, 0.95)";
      ctx.strokeStyle = "rgba(100, 105, 145, 0.75)";
      ctx.lineWidth = 4;
      roundRect(ctx, mx, my, mw, mh, 48);
      ctx.fill();
      ctx.stroke();

      [mx + 94, mx + mw - 94].forEach((sx) => {
        ctx.fillStyle = "#101a4a";
        ctx.beginPath();
        ctx.arc(sx, my + 62, 42, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = "rgba(85, 95, 155, 0.85)";
        ctx.lineWidth = 4;
        ctx.stroke();

        ctx.fillStyle = "#2b42b5";
        ctx.beginPath();
        ctx.arc(sx, my + 62, 12, 0, Math.PI * 2);
        ctx.fill();
      });

      ctx.fillStyle = "#d5a400";
      roundRect(ctx, w / 2 - 72, my - 31, 144, 52, 10);
      ctx.fill();

      ctx.strokeStyle = "#fff157";
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.fillStyle = "#ffffff";
      ctx.font = "900 26px Arial";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.shadowColor = "rgba(0,0,0,0.8)";
      ctx.shadowBlur = 4;
      ctx.fillText("Lucky", w / 2, my - 5);
      ctx.shadowBlur = 0;

      if (data.phase === "betting") {
        ctx.fillStyle = "#b28cff";
        ctx.font = "900 76px Arial";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.shadowColor = "#b28cff";
        ctx.shadowBlur = 22;
        ctx.fillText(String(data.countdown || 0), w / 2, my + 68);
        ctx.shadowBlur = 0;
      }

      // progress
      if (data.phase === "betting") {
        const px = w * 0.38;
        const py = h - 28;
        const pw = w * 0.24;
        const ph = 7;

        ctx.fillStyle = "rgba(0,0,0,0.55)";
        roundRect(ctx, px, py, pw, ph, 8);
        ctx.fill();

        const grad = ctx.createLinearGradient(px, py, px + pw, py);
        grad.addColorStop(0, "#ffe600");
        grad.addColorStop(1, "#17ff75");

        ctx.fillStyle = grad;
        roundRect(ctx, px, py, pw * progress / 100, ph, 8);
        ctx.fill();
      }

      const track = data.track || [];
      const positions = [
        [0.08, 0.23], [0.16, 0.15], [0.25, 0.14], [0.34, 0.15],
        [0.44, 0.15], [0.53, 0.15], [0.63, 0.15], [0.72, 0.15],
        [0.81, 0.15], [0.90, 0.23], [0.96, 0.44], [0.92, 0.68],
        [0.82, 0.78], [0.72, 0.78], [0.63, 0.78], [0.53, 0.78],
        [0.44, 0.78], [0.34, 0.78], [0.25, 0.78], [0.16, 0.78],
        [0.08, 0.68], [0.04, 0.44], [0.04, 0.32], [0.08, 0.23],
      ];

      track.forEach((car, index) => {
        const p = positions[index % positions.length];
        const x = p[0] * w;
        const y = p[1] * h;

        const active = data.phase === "spinning" && index === data.track_index;
        const winner =
          data.phase === "result" &&
          index === data.track_index &&
          data.winner?.key === car.key;

        drawLogoSlot(ctx, x, y, car, active, winner, t);
      });

      if (data.phase === "result" && data.winner) {
        ctx.fillStyle = "rgba(7, 8, 18, 0.76)";
        roundRect(ctx, w / 2 - 110, h / 2 - 38, 220, 76, 18);
        ctx.fill();

        ctx.strokeStyle = "rgba(255, 240, 87, 0.85)";
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.fillStyle = "#ff3b58";
        ctx.font = "900 13px Arial";
        ctx.textAlign = "center";
        ctx.fillText("WINNER", w / 2, h / 2 - 10);

        ctx.fillStyle = "#fff157";
        ctx.font = "900 26px Arial";
        ctx.fillText(data.winner.label, w / 2, h / 2 + 20);
      }

      raf = requestAnimationFrame(draw);
    }

    draw();

    return () => cancelAnimationFrame(raf);
  }, [data, progress]);

  return <canvas ref={canvasRef} className="lr-canvas-track" />;
}