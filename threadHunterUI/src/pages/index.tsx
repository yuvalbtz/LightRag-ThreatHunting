import { Link } from "@heroui/link";
import { Snippet } from "@heroui/snippet";
import { button as buttonStyles } from "@heroui/theme";
import DefaultLayout from "@/layouts/default";
import { PaperAirplaneIcon } from "@heroicons/react/24/solid";

export default function IndexPage() {
  return (
    <DefaultLayout>
      <section className="flex flex-col items-center mt-10 justify-center bg-background px-4">
        {/* Logo and Title */}
        <div className="flex flex-col items-center mb-8">

          <h1 className="text-4xl font-bold text-primary mb-2 text-center">
            ThreadHunter Chat
          </h1>
          <p className="text-lg text-gray-600 text-center max-w-xl">
            Your AI assistant for threat hunting and security research.
            <br />
            Ask questions, analyze logs, or get instant security insights.
          </p>
        </div>

        {/* Start Chatting Button */}
        <div className="flex justify-center mb-10 w-full">
          <Link
            className={buttonStyles({
              color: "primary",
              radius: "full",
              variant: "shadow",
              class: "text-lg px-8 py-4 font-semibold",
            })}
            href="/chat"
          >
            <span className="flex items-center gap-2">
              <PaperAirplaneIcon className="w-6 h-6" />
              Start Chatting
            </span>
          </Link>
        </div>

        {/* Example Prompts */}
        <div className="w-full max-w-2xl mx-auto mb-8">
          <h2 className="text-base font-semibold text-gray-700 mb-3 text-center">
            Try these prompts:
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-1 gap-4">
            <Snippet hideCopyButton hideSymbol variant="bordered">
              <span className="text-blue-600">
                How do I detect suspicious network activity in these logs?
              </span>
            </Snippet>
            <Snippet hideCopyButton hideSymbol variant="bordered">
              <span className="text-blue-600">
                Summarize this malware report for me.
              </span>
            </Snippet>
            <Snippet hideCopyButton hideSymbol variant="bordered">
              <span className="text-blue-600">
                What are the latest phishing techniques?
              </span>
            </Snippet>
            <Snippet hideCopyButton hideSymbol variant="bordered">
              <span className="text-blue-600">
                Explain the MITRE ATT&CK technique T1059.
              </span>
            </Snippet>
          </div>
        </div>
      </section>
    </DefaultLayout>
  );
}
