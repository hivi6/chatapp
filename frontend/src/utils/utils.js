function sMerge(...args) {
  let res = "";
  args.forEach((arg) => {
    if (typeof arg === "string") {
      res = res + " " + arg.trim();
    }
  });
  return res;
}

async function sleep(ms) {
  await new Promise((r) => setTimeout(r, ms));
}

export { sMerge, sleep };
