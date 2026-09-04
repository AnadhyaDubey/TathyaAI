import React, { useEffect, useRef } from "react";

export default function CurrencyCanvas({ isPaused = false }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    let animationFrameId;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };

    window.addEventListener("resize", handleResize);

    let mouseX = width / 2;
    let mouseY = height / 2;
    const handleMouseMove = (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
    };
    window.addEventListener("mousemove", handleMouseMove);

    // Note types: Navy Blue, Deep Ocean Blue, Slate Grey, Ice Blue
    const NOTE_TYPES = [
      {
        denom: "₹100",
        val: 100,
        bgColor: "rgba(30, 58, 138, 0.08)", // Navy Blue
        borderColor: "rgba(30, 58, 138, 0.28)",
        textColor: "#1e3a8a",
        accentColor: "rgba(30, 58, 138, 0.18)",
        watermark: "RESERVE BANK OF INDIA",
      },
      {
        denom: "₹500",
        val: 500,
        bgColor: "rgba(37, 99, 235, 0.08)", // Royal Blue
        borderColor: "rgba(37, 99, 235, 0.25)",
        textColor: "#2563eb",
        accentColor: "rgba(37, 99, 235, 0.18)",
        watermark: "RESERVE BANK OF INDIA",
      },
      {
        denom: "₹2000",
        val: 2000,
        bgColor: "rgba(71, 85, 105, 0.08)", // Slate Grey
        borderColor: "rgba(71, 85, 105, 0.25)",
        textColor: "#475569",
        accentColor: "rgba(71, 85, 105, 0.18)",
        watermark: "RESERVE BANK OF INDIA",
      },
    ];

    const notesCount = Math.min(Math.floor(window.innerWidth / 55), 20);
    const notes = Array.from({ length: notesCount }, () => {
      const type = NOTE_TYPES[Math.floor(Math.random() * NOTE_TYPES.length)];
      return {
        type,
        x: Math.random() * width,
        y: Math.random() * height,
        z: Math.random() * 0.7 + 0.3,
        width: 140 + Math.random() * 20,
        height: 70 + Math.random() * 10,
        vx: (Math.random() - 0.5) * 0.35,
        vy: -0.25 - Math.random() * 0.45,
        rotX: Math.random() * Math.PI * 2,
        rotY: Math.random() * Math.PI * 2,
        rotZ: (Math.random() - 0.5) * 0.5,
        vRotX: (Math.random() - 0.5) * 0.012,
        vRotY: (Math.random() - 0.5) * 0.015,
        vRotZ: (Math.random() - 0.5) * 0.008,
        opacity: Math.random() * 0.4 + 0.3,
      };
    });

    const drawNote = (note) => {
      ctx.save();

      const dx = note.x - mouseX;
      const dy = note.y - mouseY;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 180) {
        const force = (180 - dist) / 180;
        note.x += (dx / dist) * force * 1.5;
        note.y += (dy / dist) * force * 1.5;
      }

      ctx.translate(note.x, note.y);
      ctx.scale(note.z, note.z);

      const cosY = Math.cos(note.rotY);
      const sinX = Math.sin(note.rotX);
      ctx.transform(cosY, sinX * 0.2, 0, Math.cos(note.rotZ), 0, 0);

      ctx.globalAlpha = note.opacity * (0.5 + note.z * 0.5);

      const w = note.width;
      const h = note.height;
      const r = 8;

      const grad = ctx.createLinearGradient(-w / 2, -h / 2, w / 2, h / 2);
      grad.addColorStop(0, note.type.bgColor);
      grad.addColorStop(1, "rgba(255, 255, 255, 0.85)");

      ctx.fillStyle = grad;
      ctx.strokeStyle = note.type.borderColor;
      ctx.lineWidth = 1.5;

      ctx.beginPath();
      ctx.roundRect(-w / 2, -h / 2, w, h, r);
      ctx.fill();
      ctx.stroke();

      // Security stripe
      ctx.fillStyle = note.type.accentColor;
      ctx.fillRect(-w / 6, -h / 2 + 2, 8, h - 4);

      // Header text
      ctx.fillStyle = note.type.textColor;
      ctx.font = "bold 7.5px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText("RESERVE BANK OF INDIA", 0, -h / 2 + 12);

      // Denomination
      ctx.font = "bold 20px sans-serif";
      ctx.textAlign = "left";
      ctx.fillText(note.type.denom, -w / 2 + 10, h / 2 - 12);

      // Watermark text
      ctx.font = "6px sans-serif";
      ctx.fillStyle = "rgba(71, 85, 105, 0.35)";
      ctx.textAlign = "center";
      ctx.fillText(note.type.watermark, 10, 2);

      // Circle watermark right
      ctx.beginPath();
      ctx.arc(w / 2 - 20, 0, 14, 0, Math.PI * 2);
      ctx.strokeStyle = note.type.borderColor;
      ctx.lineWidth = 1;
      ctx.stroke();

      ctx.fillStyle = note.type.textColor;
      ctx.font = "bold 12px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText("₹", w / 2 - 20, 4);

      ctx.restore();
    };

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      if (!isPaused) {
        notes.forEach((note) => {
          note.x += note.vx;
          note.y += note.vy;
          note.rotX += note.vRotX;
          note.rotY += note.vRotY;
          note.rotZ += note.vRotZ;

          if (note.y < -100) {
            note.y = height + 80;
            note.x = Math.random() * width;
          }
          if (note.x < -100) note.x = width + 80;
          if (note.x > width + 100) note.x = -80;

          drawNote(note);
        });
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener("resize", handleResize);
      window.removeEventListener("mousemove", handleMouseMove);
      cancelAnimationFrame(animationFrameId);
    };
  }, [isPaused]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        pointerEvents: "none",
        zIndex: 0,
      }}
    />
  );
}
