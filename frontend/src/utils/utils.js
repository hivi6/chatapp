function sMerge(...args) {
  let res = "";
  args.forEach((arg) => {
    if (typeof arg === "string") {
      res = res + " " + arg.trim();
    }
  });
  return res;
}

export { sMerge };
