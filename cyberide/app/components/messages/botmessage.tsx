// import { ConversationMessage } from "@/app/lib/types";
// import { BotProfile } from "../botprofile";
// import { CodeBlock } from "./codeblock";
// import { useEffect, useRef } from "react";
// import MemoryWidget, { MemoryWidgetProps } from "../memorywidget";
// import { IBM } from "@/app/lib/fonts";

// interface BotProps {
//   message: ConversationMessage;
//   time: number;
//   botName: string;
//   suggestions: MemoryWidgetProps[];
// }

// // Helper to parse message with inline code blocks
// function parseMessageWithCode(message: string) {
//   const codeRegex = /```(?:([\w+-]*)\n)?([\s\S]*?)```/g;
//   const elements = [];
//   let lastIndex = 0;
//   let match;
//   let key = 0;

//   while ((match = codeRegex.exec(message)) !== null) {
//     const [fullMatch, language = "plaintext", code] = match;
//     const textBefore = message.slice(lastIndex, match.index);

//     if (textBefore.trim()) {
//       elements.push(
//         <p className="whitespace-pre-line leading-relaxed mb-2" key={`text-${key++}`}>
//           {textBefore}
//         </p>
//       );
//     }

//     elements.push(
//       <div className="my-2 w-full" key={`code-${key++}`}>
//         <CodeBlock code={code.trim()} language={language} />
//       </div>
//     );

//     lastIndex = match.index + fullMatch.length;
//   }

//   const remainingText = message.slice(lastIndex);
//   if (remainingText.trim()) {
//     elements.push(
//       <p className="whitespace-pre-line leading-relaxed" key={`text-${key++}`}>
//         {remainingText}
//       </p>
//     );
//   }

//   return elements;
// }


// export function BotMessage(props: BotProps) {
//   const progressbar = useRef(null as any as HTMLDivElement);
//   const start = useRef(new Date());
//   useEffect(() => {
//     if (progressbar.current == null) return;
//     start.current = new Date();
//     let int = setInterval(() => {
//       let progress =
//         ((new Date().getTime() - start.current.getTime()) /
//           ((props.time + 1) * 1000)) *
//         100;
//       progressbar.current.style.width = progress + "%";
//       if (progress > 100) clearTimeout(int);
//     }, 60);
//   }, []);
//   useEffect(() => {
//     const el = progressbar.current;
//     if (!el) return;
//     el.style.opacity = "1";
//   }, []);
//   // console.log("Parsed message output:", parseMessageWithCode(props.message.text));
//   console.log("Raw message text:", props.message.text);

//   return (
//     <div className="bg-gray-50/90 border border-gray-200 text-gray-800 flex flex-row items-start w-[80%] gap-2 rounded-2xl shadow-sm p-4 transition-transform duration-200 hover:-translate-y-0.5 hover:shadow-md animate-fade-in">
//       <BotProfile name="R E" />
//       <div className="w-full h-full flex flex-col items-start gap-2">
//         <div className="w-full flex flex-row items-center ">
//           <p className={`grow-0 text-black ${IBM.className} text-sm`}>
//             {props.botName}
//           </p>
//           {/* <p className={`grow-0 text-black ${IBM.className} text-sm`}>[try to answer in {props.time} seconds]</p> */}
//         </div>
//         {/* <p className="w-full whitespace-pre-line leading-relaxed">
//           {props.message.text}
//         </p> */}
//         <div className="w-full">{parseMessageWithCode(props.message.text)}</div>
//         {props.suggestions.length > 0 && (
//           <>
//             <p className="text-sm text-black mb-2 mt-2">suggested code</p>
//             <div className="flex gap-3 overflow-x-auto pb-2 fade-scrollbar">
//               {props.suggestions.map((suggestion, i) => (
//                 <div className="min-w-[180px] animate-fade-in" key={i}>
//                   <MemoryWidget {...suggestion} />
//                 </div>
//               ))}
//             </div>
//           </>
//         )}
//       </div>
//     </div>
//   );
// }


import { useEffect, useRef } from "react";

interface ConversationMessage {
  text: string;
  sentByUser: boolean;
}

interface MemoryWidgetProps {
  title: string;
  description: string;
}

interface BotProps {
  message: ConversationMessage;
  time: number;
  botName: string;
  suggestions: MemoryWidgetProps[];
}

// Simplified BotProfile component
function BotProfile({ name }: { name: string }) {
  return (
    <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-xs font-bold">
      {name}
    </div>
  );
}

// Simplified MemoryWidget component
function MemoryWidget({ title, description }: MemoryWidgetProps) {
  return (
    <div className="p-3 bg-white border rounded-lg">
      <p className="font-semibold text-sm">{title}</p>
      <p className="text-xs text-gray-600">{description}</p>
    </div>
  );
}

function CodeBlock({ code, language }: { code: string; language: string }) {
  return (
    <pre className="bg-black text-white p-4 rounded-md overflow-x-auto text-sm">
      <code className={`language-${language}`}>{code}</code>
    </pre>
  );
}

// Helper to parse message with inline code blocks
function parseMessageWithCode(message: string) {
  console.log("🔍 [parseMessageWithCode] Input message:", message);
  console.log("🔍 [parseMessageWithCode] Message length:", message.length);
  console.log("🔍 [parseMessageWithCode] Message type:", typeof message);
  
  const codeRegex = /```(?:([\w+-]*)\n)?([\s\S]*?)```/g;
  const elements = [];
  let lastIndex = 0;
  let match;
  let key = 0;

  while ((match = codeRegex.exec(message)) !== null) {
    console.log("✅ [parseMessageWithCode] Found code block!", match);
    const [fullMatch, language = "plaintext", code] = match;
    const textBefore = message.slice(lastIndex, match.index);

    if (textBefore.trim()) {
      console.log("📝 [parseMessageWithCode] Adding text:", textBefore);
      elements.push(
        <p className="whitespace-pre-line leading-relaxed mb-2" key={`text-${key++}`}>
          {textBefore}
        </p>
      );
    }

    console.log("💻 [parseMessageWithCode] Adding code block with language:", language);
    elements.push(
      <div className="my-2 w-full" key={`code-${key++}`}>
        <CodeBlock code={code.trim()} language={language} />
      </div>
    );

    lastIndex = match.index + fullMatch.length;
  }

  const remainingText = message.slice(lastIndex);
  if (remainingText.trim()) {
    console.log("📝 [parseMessageWithCode] Adding remaining text:", remainingText);
    elements.push(
      <p className="whitespace-pre-line leading-relaxed" key={`text-${key++}`}>
        {remainingText}
      </p>
    );
  }

  console.log("🎯 [parseMessageWithCode] Total elements created:", elements.length);
  return elements;
}

export function BotMessage(props: BotProps) {
  const progressbar = useRef<HTMLDivElement>(null);
  const start = useRef(new Date());
  
  useEffect(() => {
    if (progressbar.current == null) return;
    start.current = new Date();
    let int = setInterval(() => {
      let progress =
        ((new Date().getTime() - start.current.getTime()) /
          ((props.time + 1) * 1000)) *
        100;
      if (progressbar.current) {
        progressbar.current.style.width = progress + "%";
      }
      if (progress > 100) clearTimeout(int);
    }, 60);
  }, [props.time]);
  
  useEffect(() => {
    const el = progressbar.current;
    if (!el) return;
    el.style.opacity = "1";
  }, []);
  
  console.log("🤖 [BotMessage] Raw message text:", props.message.text);
  console.log("🤖 [BotMessage] Message object:", props.message);
  
  const parsedContent = parseMessageWithCode(props.message.text);
  console.log("🤖 [BotMessage] Parsed content:", parsedContent);

  return (
    <div className="bg-gray-50/90 border border-gray-200 text-gray-800 flex flex-row items-start w-[80%] gap-2 rounded-2xl shadow-sm p-4 transition-transform duration-200 hover:-translate-y-0.5 hover:shadow-md animate-fade-in">
      <BotProfile name="RE" />
      <div className="w-full h-full flex flex-col items-start gap-2">
        <div className="w-full flex flex-row items-center">
          <p className="grow-0 text-black text-sm font-mono">
            {props.botName}
          </p>
        </div>
        <div className="w-full">{parsedContent}</div>
        {props.suggestions.length > 0 && (
          <>
            <p className="text-sm text-black mb-2 mt-2">suggested code</p>
            <div className="flex gap-3 overflow-x-auto pb-2">
              {props.suggestions.map((suggestion, i) => (
                <div className="min-w-[180px] animate-fade-in" key={i}>
                  <MemoryWidget {...suggestion} />
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}