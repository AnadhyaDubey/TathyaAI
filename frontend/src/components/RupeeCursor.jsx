import React, { useEffect, useRef } from "react";

export default function RupeeCursor() {
  const badgeRef = useRef(null);
  const auraRef = useRef(null);

  useEffect(() => {
    let animFrame;
    let targetX = -100;
    let targetY = -100;

    let badgeX = -100;
    let badgeY = -100;

    let auraX = -100;
    let auraY = -100;

    const handleMouseMove = (e) => {
      targetX = e.clientX;
      targetY = e.clientY;

      const target = e.target;
      const isInteractive =
        target.closest("button") ||
        target.closest("a") ||
        target.closest("input") ||
        target.closest("select") ||
        target.closest(".stat-card") ||
        target.closest(".case-row") ||
        target.closest(".kpi-card") ||
        target.closest(".payload-card");

      if (badgeRef.current && auraRef.current) {
        if (isInteractive) {
          badgeRef.current.classList.add("hovered");
          auraRef.current.classList.add("hovered");
        } else {
          badgeRef.current.classList.remove("hovered");
          auraRef.current.classList.remove("hovered");
        }
      }
    };

    const handleMouseDown = () => {
      if (badgeRef.current && auraRef.current) {
        badgeRef.current.classList.add("clicking");
        auraRef.current.classList.add("clicking");
      }
    };

    const handleMouseUp = () => {
      if (badgeRef.current && auraRef.current) {
        badgeRef.current.classList.remove("clicking");
        auraRef.current.classList.remove("clicking");
      }
    };

    window.addEventListener("mousemove", handleMouseMove, { passive: true });
    window.addEventListener("mousedown", handleMouseDown, { passive: true });
    window.addEventListener("mouseup", handleMouseUp, { passive: true });

    // Hardware accelerated RAF loop with dual-lerp physics (tight for badge, smooth trailing for aura)
    const animate = () => {
      // Fast response for badge (0.35 factor)
      badgeX += (targetX - badgeX) * 0.35;
      badgeY += (targetY - badgeY) * 0.35;

      // Silky trailing response for aura (0.18 factor)
      auraX += (targetX - auraX) * 0.18;
      auraY += (targetY - auraY) * 0.18;

      if (badgeRef.current) {
        badgeRef.current.style.transform = `translate3d(${badgeX - 14}px, ${badgeY - 14}px, 0)`;
      }
      if (auraRef.current) {
        auraRef.current.style.transform = `translate3d(${auraX - 22}px, ${auraY - 22}px, 0)`;
      }

      animFrame = requestAnimationFrame(animate);
    };

    animFrame = requestAnimationFrame(animate);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mousedown", handleMouseDown);
      window.removeEventListener("mouseup", handleMouseUp);
      cancelAnimationFrame(animFrame);
    };
  }, []);

  return (
    <>
      <div ref={auraRef} className="rupee-cursor-aura" />
      <div ref={badgeRef} className="rupee-cursor-badge">
        ₹
      </div>
    </>
  );
}
