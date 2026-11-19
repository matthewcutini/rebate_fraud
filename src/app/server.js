const http = require("node:http");

const port = Number(process.env.DATABRICKS_APP_PORT || 8000);

const server = http.createServer((request, response) => {
  if (request.url === "/health") {
    response.writeHead(200, { "content-type": "application/json" });
    response.end(JSON.stringify({ status: "ok" }));
    return;
  }

  response.writeHead(200, { "content-type": "text/plain; charset=utf-8" });
  response.end("Rebate Fraud Operations\n");
});

server.listen(port, "0.0.0.0");
