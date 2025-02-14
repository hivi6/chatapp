import { useEffect, useState } from "react";
import { FaRegLemon } from "react-icons/fa";
import { Progress } from "radix-ui";

const ProgressBar = ({ progress }) => (
  <div className="border-2 rounded-full border-primary">
    <Progress.Root
      value={progress}
      className="overflow-hidden rounded-full border-2 border-base-100 w-[400px] h-[10px]"
    >
      <Progress.Indicator
        className="duration-500 size-full bg-primary"
        style={{ transform: `translateX(-${100 - progress}%)` }}
      />
    </Progress.Root>
  </div>
);

function App() {
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState("Hello");

  useEffect(() => {
    const timer = setTimeout(() => {
      setProgress(80);
      setMessage("Bye");
    }, 500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <>
      <div className="h-screen w-screen bg-base-100 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="flex text-primary text-6xl gap-4">
            <FaRegLemon />
            <div>Chatapp</div>
          </div>
          <ProgressBar progress={progress} />
          <div className="text-lg text-accent-content transition-all">
            {message}
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
