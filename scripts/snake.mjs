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
    colorDots: ["#ebedf0", "#f5d0fe", "#f0abfc", "#e879f9", "#c026d3"],
    colorSnake: "#86198f",
  },
  "snake-dark.svg": {
    colorDotBorder: "#ffffff08",
    colorEmpty: "#161b22",
    colorDots: ["#161b22", "#4a1450", "#86198f", "#c026d3", "#e879f9"],
    colorSnake: "#f0abfc",
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
