const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

// Ekranni to'liq egallash
function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.addEventListener("resize", resize);
resize();

// Sichqoncha joylashuvi
let mouse = { x: canvas.width / 2, y: canvas.height / 2 };
document.addEventListener("mousemove", e => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
});

// Chayonning har bir bo'g'imi uchun (Segment)
class Segment {
    constructor(x, y, length, radius) {
        this.x = x;
        this.y = y;
        this.length = length;
        this.radius = radius;
        this.angle = 0;
    }

    // O'zidan oldingi segmentga asosan ergashishi
    follow(targetX, targetY) {
        let dx = targetX - this.x;
        let dy = targetY - this.y;
        this.angle = Math.atan2(dy, dx);

        this.x = targetX - Math.cos(this.angle) * this.length;
        this.y = targetY - Math.sin(this.angle) * this.length;
    }
}

class ScorpionSkeleton {
    constructor(x, y) {
        this.segments = [];
        this.numSegments = 22; // Chayon uzunligi
        this.speed = 4.5;

        this.headX = x;
        this.headY = y;

        // Qismlarni (bo'g'imlarni) shakllantiramiz
        for (let i = 0; i < this.numSegments; i++) {
            let radius = 8;

            // Kengaytirilgan tanasi (qorni va ko'kragi)
            if (i > 2 && i < 11) {
                radius = 16 - Math.abs(6 - i) * 1.5;
            }
            // Dumini ingichkalashib borishi
            if (i >= 11) {
                radius = Math.max(3, 14 - (i - 10) * 1.2);
            }

            let len = i === 0 ? 0 : 12; // Segmentlar orasidagi masofa
            this.segments.push(new Segment(x, y, len, radius));
        }
    }

    update() {
        // Boshning sichqoncha tomon harakatlanishi
        let dx = mouse.x - this.headX;
        let dy = mouse.y - this.headY;
        let dist = Math.hypot(dx, dy);

        if (dist > this.speed) {
            this.headX += (dx / dist) * this.speed;
            this.headY += (dy / dist) * this.speed;
        }

        // Qolgan tananing boshga ergashish mantig'i
        this.segments[0].follow(this.headX, this.headY);
        for (let i = 1; i < this.numSegments; i++) {
            this.segments[i].follow(this.segments[i - 1].x, this.segments[i - 1].y);
        }
    }

    draw(ctx) {
        // 1. Oyoqlarni chizish
        ctx.strokeStyle = "#888";
        ctx.lineWidth = 2;
        let time = Date.now() / 150; // Harakatlanish effekti uchun

        for (let i = 3; i <= 9; i += 2) {
            let seg = this.segments[i];
            let prevSeg = this.segments[i - 1];

            // Segment yo'nalish burchagini aniqlash
            let angle = Math.atan2(prevSeg.y - seg.y, prevSeg.x - seg.x);
            let perpAngle1 = angle + Math.PI / 1.5;
            let perpAngle2 = angle - Math.PI / 1.5;

            // Yurganda tebranish (oyoq otishi)
            let legMotion = Math.sin(time + i) * 10;
            let legLength = 30;

            // Chap oyoq
            ctx.beginPath();
            ctx.moveTo(seg.x, seg.y);
            ctx.lineTo(seg.x + Math.cos(perpAngle1) * legLength + Math.cos(angle) * legMotion,
                seg.y + Math.sin(perpAngle1) * legLength + Math.sin(angle) * legMotion);
            ctx.stroke();

            // O'ng oyoq
            ctx.beginPath();
            ctx.moveTo(seg.x, seg.y);
            ctx.lineTo(seg.x + Math.cos(perpAngle2) * legLength - Math.cos(angle) * legMotion,
                seg.y + Math.sin(perpAngle2) * legLength - Math.sin(angle) * legMotion);
            ctx.stroke();
        }

        // 2. Umurtqani (markaziy o'qni) chizish
        ctx.beginPath();
        for (let i = 0; i < this.numSegments; i++) {
            if (i === 0) ctx.moveTo(this.segments[i].x, this.segments[i].y);
            else ctx.lineTo(this.segments[i].x, this.segments[i].y);
        }
        ctx.strokeStyle = "#ccc";
        ctx.lineWidth = 4;
        ctx.stroke();

        // 3. Segment (Skelet suyaklarini) doiralar bilan shakllantirish
        for (let i = 0; i < this.numSegments; i++) {
            let seg = this.segments[i];
            ctx.beginPath();
            ctx.arc(seg.x, seg.y, seg.radius, 0, Math.PI * 2);

            // Bosh qismi (qizil), Dum uchidagi nish (sariq), tanasi (qora-sariq)
            if (i === 0) {
                ctx.fillStyle = "#ff3333"; // Bosh
            } else if (i === this.numSegments - 1) {
                ctx.fillStyle = "#ffea00"; // Stinger (Dum uchi)
            } else {
                ctx.fillStyle = "#111"; // Skelet tana rangi
            }

            ctx.fill();
            ctx.strokeStyle = i === 0 || i === this.numSegments - 1 ? "#fff" : "#888";
            ctx.lineWidth = 1.5;
            ctx.stroke();
        }

        // 4. Katta Old qisqichlari (Pincers)
        let headSeg = this.segments[0];
        let neckSeg = this.segments[2];
        let pincerAngle = Math.atan2(headSeg.y - neckSeg.y, headSeg.x - neckSeg.x);

        let pincerMotion = Math.sin(time * 0.5) * 0.2; // Qisqichlarning tez-tez harakati

        // Chap qisqich
        ctx.beginPath();
        ctx.moveTo(headSeg.x, headSeg.y);
        ctx.lineTo(headSeg.x + Math.cos(pincerAngle - 0.8 + pincerMotion) * 35,
            headSeg.y + Math.sin(pincerAngle - 0.8 + pincerMotion) * 35);
        ctx.strokeStyle = "#ff3333";
        ctx.lineWidth = 6;
        ctx.stroke();

        // O'ng qisqich
        ctx.beginPath();
        ctx.moveTo(headSeg.x, headSeg.y);
        ctx.lineTo(headSeg.x + Math.cos(pincerAngle + 0.8 - pincerMotion) * 35,
            headSeg.y + Math.sin(pincerAngle + 0.8 - pincerMotion) * 35);
        ctx.stroke();
    }
}

const scorpion = new ScorpionSkeleton(canvas.width / 2, canvas.height / 2);

// O'yinning asosiy animatsiya tsikli
function gameLoop() {
    // Qop qora fonga ega qilish uchu har freymni tozalash
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    scorpion.update();
    scorpion.draw(ctx);

    requestAnimationFrame(gameLoop);
}

gameLoop();
