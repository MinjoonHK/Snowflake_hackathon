/**
 * Snowflake Managed MCP Server → stdio 프록시
 * mcp-remote의 OAuth 문제를 우회하여 PAT 토큰으로 직접 연결합니다.
 */
import { createInterface } from "readline";

const SF_MCP_URL = process.env.SF_MCP_URL;
const SF_PAT_TOKEN = process.env.SF_PAT_TOKEN;

if (!SF_MCP_URL || !SF_PAT_TOKEN) {
  process.stderr.write("ERROR: SF_MCP_URL and SF_PAT_TOKEN env vars required\n");
  process.exit(1);
}

const headers = {
  "Content-Type": "application/json",
  "Authorization": `Bearer ${SF_PAT_TOKEN}`,
};

// Snowflake MCP 서버에 JSON-RPC 요청 전송
async function sendToSnowflake(jsonrpcMessage) {
  try {
    const res = await fetch(SF_MCP_URL, {
      method: "POST",
      headers,
      body: JSON.stringify(jsonrpcMessage),
    });

    if (!res.ok) {
      const text = await res.text();
      process.stderr.write(`Snowflake HTTP ${res.status}: ${text}\n`);

      // 에러 응답 반환
      if (jsonrpcMessage.id !== undefined) {
        return {
          jsonrpc: "2.0",
          id: jsonrpcMessage.id,
          error: { code: -32000, message: `Snowflake error: ${res.status} ${text}` },
        };
      }
      return null;
    }

    const contentType = res.headers.get("content-type") || "";

    // JSON 응답
    if (contentType.includes("application/json")) {
      return await res.json();
    }

    // 텍스트 응답 (일부 Snowflake 응답)
    const text = await res.text();
    try {
      return JSON.parse(text);
    } catch {
      process.stderr.write(`Non-JSON response: ${text.slice(0, 200)}\n`);
      if (jsonrpcMessage.id !== undefined) {
        return {
          jsonrpc: "2.0",
          id: jsonrpcMessage.id,
          error: { code: -32000, message: `Unexpected response: ${text.slice(0, 200)}` },
        };
      }
      return null;
    }
  } catch (err) {
    process.stderr.write(`Fetch error: ${err.message}\n`);
    if (jsonrpcMessage.id !== undefined) {
      return {
        jsonrpc: "2.0",
        id: jsonrpcMessage.id,
        error: { code: -32000, message: err.message },
      };
    }
    return null;
  }
}

// stdio로 JSON-RPC 메시지 읽기/쓰기
const rl = createInterface({ input: process.stdin });

rl.on("line", async (line) => {
  if (!line.trim()) return;

  let msg;
  try {
    msg = JSON.parse(line);
  } catch {
    process.stderr.write(`Invalid JSON: ${line.slice(0, 100)}\n`);
    return;
  }

  process.stderr.write(`→ ${msg.method || "response"} (id=${msg.id})\n`);

  const result = await sendToSnowflake(msg);
  if (result) {
    process.stdout.write(JSON.stringify(result) + "\n");
    process.stderr.write(`← response (id=${result.id})\n`);
  }
});

rl.on("close", () => process.exit(0));

process.stderr.write("Snowflake MCP Proxy started\n");
