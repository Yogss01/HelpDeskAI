
const { Readable } = require("node:stream");

module.exports = async function handler(req, res) {
  const requestedPath = String(req.query.path || "")
    .replace(/^\/+|\/+$/g, "");

  // Allow the main API routes and individual ticket routes.
  const isAllowedPath =
    ["health", "chat", "tickets", "analytics", "documents"]
      .includes(requestedPath) ||
    /^tickets\/[a-zA-Z0-9_-]+$/.test(requestedPath);

  if (!isAllowedPath) {
    return res.status(404).json({
      detail: "API route not found",
    });
  }

  const backendUrl = process.env.BACKEND_URL;
  const apiKey = process.env.HELPDESK_API_KEY;

  if (!backendUrl || !apiKey) {
    return res.status(500).json({
      detail: "Server environment is not configured",
    });
  }

  let target;

  try {
    target = new URL(`/api/${requestedPath}`, backendUrl);
  } catch {
    return res.status(500).json({
      detail: "Invalid backend URL configuration",
    });
  }

  // Preserve query parameters such as ?filename=...
  for (const [key, value] of Object.entries(req.query)) {
    if (key !== "path" && typeof value === "string") {
      target.searchParams.set(key, value);
    }
  }

  const headers = {
    "X-API-Key": apiKey,
  };

  if (req.headers["content-type"]) {
    headers["content-type"] = req.headers["content-type"];
  }

  try {
    const options = {
      method: req.method,
      headers,
      redirect: "manual",
    };

    // Forward the original request body, including file uploads.
    if (!["GET", "HEAD"].includes(req.method)) {
      options.body = Readable.toWeb(req);
      options.duplex = "half";
    }

    const upstream = await fetch(target, options);

    res.status(upstream.status);

    const contentType = upstream.headers.get("content-type");

    if (contentType) {
      res.setHeader("content-type", contentType);
    }

    const body = Buffer.from(await upstream.arrayBuffer());

    return res.send(body);
  } catch (error) {
    console.error(
      "Backend proxy request failed:",
      error.message
    );

    return res.status(502).json({
      detail: "Unable to reach the HelpDeskAI backend",
    });
  }
};

module.exports.config = {
  api: {
    bodyParser: false,
  },
};
