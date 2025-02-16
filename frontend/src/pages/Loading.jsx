import { useEffect, useState } from "react";
import { FaRegLemon } from "react-icons/fa";
import { Progress } from "radix-ui";
import { useNavigate } from "react-router-dom";

import { ping, verify } from "../services/httpClient";
import { sleep } from "../utils/utils";

const ProgressBar = ({ progress }) => (
  <div className="border-2 rounded-full border-primary">
    <Progress.Root
      value={progress}
      className="overflow-hidden rounded-full border-2 border-black w-[400px] h-[10px]"
    >
      <Progress.Indicator
        className="duration-500 size-full bg-secondary"
        style={{ transform: `translateX(-${100 - progress}%)` }}
      />
    </Progress.Root>
  </div>
);

export default function Loading() {
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState("> ... <");
  const navigate = useNavigate();

  useEffect(() => {
    loadStuff();
  }, []);

  async function checkServerConnection() {
    const { data, error } = await ping();
    if (error !== undefined) {
      console.log(`checkServerConnection error: ${error}`);
      await sleep(500);
      navigate("/login");
    } else {
      console.log(`checkServerConnection success: ${data}`);
    }
  }

  async function verifyUser() {
    const { data, error } = await verify();
    if (error !== undefined) {
      console.log(`verifyUser error: ${error}`);
      await sleep(500);
      navigate("/login");
    } else {
      console.log(`verifyUser success: ${data}`);
    }
  }

  async function loadStuff() {
    // First set Progress to zero
    setProgress(0);

    // Checking if server is active
    await sleep(500);
    setMessage("> Connecting to server <");
    setProgress((prev) => prev + (100 - prev) / 2);
    await checkServerConnection();

    // Verifying user
    await sleep(500);
    setMessage("> Verifying user <");
    setProgress((prev) => prev + (100 - prev) / 2);
    await verifyUser();

    // TODO: Load user information

    // TODO: Load user contacts

    // TODO: Load user conversations

    // TODO: Load user messages

    // Show Accept message
    await sleep(500);
    setMessage("> Accepted <");
    setProgress(100);

    // TODO: Change to dashboard
    await sleep(500);
  }

  return (
    <div className="h-screen w-screen bg-base-100 flex items-center justify-center select-none">
      <div className="flex flex-col items-center gap-4">
        <div className="flex text-primary text-6xl gap-4">
          <FaRegLemon />
          <div>Chatapp</div>
        </div>
        <ProgressBar progress={progress} />
        <div className="text-sm text-accent-content transition-all">
          {message}
        </div>
      </div>
    </div>
  );
}
