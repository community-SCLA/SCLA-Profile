// No includes, custom configuration, network fetches, or HTML output.
const fs = require("node:fs");
(async () => {
  try {
    const source = fs.readFileSync(0, "utf8");
    if (Buffer.byteLength(source, "utf8") > 100000 || /<mj-(include|raw)\b/i.test(source)) throw Error();
    const library = require("mjml");
    const compile = library.default || library;
    const result = await compile(source, {
      validationLevel: "strict",
      ignoreIncludes: true,
      allowIncludes: false,
      useMjmlConfigOptions: false,
    });
    if (!result.html || result.errors?.length) throw Error();
    process.stdout.write("valid\n");
  } catch {
    process.stderr.write("MJML validation failed.\n");
    process.exitCode = 1;
  }
})();
