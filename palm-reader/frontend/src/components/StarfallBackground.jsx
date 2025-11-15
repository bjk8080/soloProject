import React, { useEffect, useRef } from "react";

export default function StarfallBackground() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    resize();
    window.addEventListener("resize", resize);

    // 기본 별들
    const stars = [];
    const maxStars = 120;

    // 이벤트 별
    let specialStar = null;

    class Star {
      constructor() {
        this.reset();
      }
      reset() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * -canvas.height;
        this.speed = 2 + Math.random() * 4;
        this.length = 10 + Math.random() * 20;
        this.opacity = 0.5 + Math.random() * 0.5;
      }
      update() {
        this.y += this.speed;
        if (this.y > canvas.height) this.reset();
      }
      draw() {
        ctx.strokeStyle = `rgba(255,255,255,${this.opacity})`;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(this.x, this.y);
        ctx.lineTo(this.x - this.length * 0.4, this.y - this.length);
        ctx.stroke();
      }
    }

    class SpecialStar {
      constructor() {
        // 노란색 “특별 별똥별”
        this.x = Math.random() * canvas.width;
        this.y = -50;
        this.speed = 8 + Math.random() * 4;
        this.length = 40 + Math.random() * 30;
        this.opacity = 1;
        this.active = true;
      }
      update() {
        this.y += this.speed;
        this.x += this.speed * 0.4;
        if (this.y > canvas.height + 100) {
          this.active = false;
        }
      }
      draw() {
        ctx.strokeStyle = `rgba(255,215,0,${this.opacity})`; // 금색
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(this.x, this.y);
        ctx.lineTo(this.x - this.length * 0.6, this.y - this.length);
        ctx.stroke();
      }
    }

    for (let i = 0; i < maxStars; i++) stars.push(new Star());

    // 랜덤하게 특별 별 생성
    function maybeCreateSpecialStar() {
      if (!specialStar && Math.random() < 0.025) {
        specialStar = new SpecialStar();
      }
    }

    function animate() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      stars.forEach((s) => {
        s.update();
        s.draw();
      });

      // 특별 별똥별 처리
      if (specialStar) {
        specialStar.update();
        specialStar.draw();
        if (!specialStar.active) {
          specialStar = null;
        }
      } else {
        maybeCreateSpecialStar();
      }

      requestAnimationFrame(animate);
    }

    animate();

    return () => {
      window.removeEventListener("resize", resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed top-0 left-0 w-full h-full -z-10"
    />
  );
}
