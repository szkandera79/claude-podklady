import Anthropic from "@anthropic-ai/sdk";
import { handleRequest, type Env, type StreamFactory } from "./handler";

const anthropicStream: StreamFactory = (env, params) => {
  const client = new Anthropic({ apiKey: env.ANTHROPIC_API_KEY, maxRetries: 1 });
  // `fallbacks: "default"` je novější než typy SDK, proto přetypování.
  const stream = client.beta.messages.stream(params as any);
  return { events: stream, final: () => stream.finalMessage(), abort: () => stream.abort() };
};

export default {
  fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    return handleRequest(request, env, ctx, anthropicStream);
  },
} satisfies ExportedHandler<Env>;
