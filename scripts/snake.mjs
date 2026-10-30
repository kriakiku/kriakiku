import { readFileSync, writeFileSync } from "node:fs";
import { generateSnakeAnimation } from "generate-snake-animation";

const dir = process.argv[2] ?? "dist";
const levels = JSON.parse(readFileSync(`${dir}/levels.json`, "utf8"));

// The GitLab source reads a { date: count } calendar; feeding it levels 0..4 keeps the combined GitHub + GitLab grid.
globalThis.fetch = async () => Response.json(levels);

const themes = {
  "snake.svg": {
    colorDotBorder: "#1b1f230a",
    colorEmpty: "#ebedf0",
    colorDots: ["#ebedf0", "#ffd8b0", "#ffb070", "#ff8a33", "#e8590c"],
    colorSnake: "#c2410c",
  },
  "snake-dark.svg": {
    colorDotBorder: "#ffffff08",
    colorEmpty: "#161b22",
    colorDots: ["#161b22", "#4a2410", "#8a3d0f", "#d95a0b", "#ff7a1a"],
    colorSnake: "#ffb547",
  },
};

const names = Object.keys(themes);
const svgs = await generateSnakeAnimation(
  { platform: "gitlab", username: "kriakiku" },
  names.map((name) => ({
    format: "svg",
    drawOptions: { sizeCell: 16, sizeDot: 12, sizeDotBorderRadius: 2, ...themes[name] },
    animationOptions: { frameByStep: 1, stepDurationMs: 100 },
  })),
);
names.forEach((name, i) => writeFileSync(`${dir}/${name}`, svgs[i]));
