import { Tabs } from "radix-ui";
import { useRef, useState } from "react";
import { FaRegLemon } from "react-icons/fa";
import { useNavigate } from "react-router-dom";

import { sMerge, sleep } from "../utils/utils";
import { login, register } from "../services/httpClient";

export default function Login() {
  const [currentTab, setCurrentTab] = useState("login");
  const [errorMsg, setErrorMsg] = useState("\xa0");
  const [buttonColor, setButtonColor] = useState("bg-accent");
  const [timeoutId, setTimeoutId] = useState(null);
  const usernameRef = useRef();
  const passwordRef = useRef();
  const fullnameRef = useRef();
  const navigate = useNavigate();

  function resetButtonAndMsg() {
    if (timeoutId !== null) clearTimeout(timeoutId);
    setErrorMsg("\xa0");
    setButtonColor("bg-accent");
    setTimeoutId(null);
  }

  function produceError(msg) {
    setErrorMsg(msg);
    setButtonColor("bg-error");

    // Reset after 5 seconds
    if (timeoutId !== null) clearTimeout(timeoutId);
    const temp = setTimeout(() => {
      setErrorMsg("\xa0");
      setButtonColor("bg-accent");
      setTimeoutId(null);
    }, 2000);
    setTimeoutId(temp);
  }

  async function handleLogin() {
    const { data, error } = await login({
      username: usernameRef.current.value,
      password: passwordRef.current.value,
    });
    if (error !== undefined) {
      produceError(`* ${error}`);
      return;
    }

    setButtonColor("bg-info/50");
    await sleep(1000);
    resetButtonAndMsg();

    navigate("/loading");
  }

  async function handleRegister() {
    const { data, error } = await register({
      username: usernameRef.current.value,
      password: passwordRef.current.value,
      fullname: fullnameRef.current.value,
    });
    if (error !== undefined) {
      produceError(`* ${error}`);
      return;
    }

    setButtonColor("bg-info/50");
    await sleep(1000);
    resetButtonAndMsg();

    setCurrentTab("login");
  }

  return (
    <div className="h-screen w-screen bg-base-100 flex flex-col gap-6 items-center justify-center">
      {/* Chatapp Logo */}
      <div className="flex text-primary hover:text-primary/70 text-6xl gap-4 transition-all duration-250">
        <FaRegLemon />
        <div className="select-none">Chatapp</div>
      </div>

      <div className="p-2 border-2 border-secondary rounded-xl bg-black w-lg ">
        <Tabs.Root
          className="text-accent-content flex flex-col bg-base-200 border-2 border-primary rounded-md"
          value={currentTab}
          onValueChange={(value) => {
            resetButtonAndMsg();
            setCurrentTab(value);
          }}
        >
          <Tabs.List className="flex items-center justify-center border-b-2 border-b-primary">
            <Tabs.Trigger
              value="login"
              className={sMerge(
                "flex-1 shrink-0 h-12 hover:bg-base-100 border-transparent rounded-tl-md border-r-2 border-r-primary hover:text-accent-content/80",
                currentTab === "login" &&
                  "bg-base-100 underline underline-offset-2"
              )}
            >
              Login
            </Tabs.Trigger>
            <Tabs.Trigger
              value="register"
              className={sMerge(
                "flex-1 shrink-0 h-12 hover:bg-base-100 border-transparent rounded-tr-md hover:text-accent-content/80",
                currentTab === "register" &&
                  "bg-base-100 underline underline-offset-2"
              )}
            >
              Register
            </Tabs.Trigger>
          </Tabs.List>

          {/* Login Form */}
          <Tabs.Content
            value="login"
            className="grow p-5 flex flex-col gap-2 h-fit"
          >
            <fieldset className="flex flex-col">
              <label className="h-8 text-accent-content/90">- Username</label>
              <input
                ref={usernameRef}
                className="border-2 h-10 p-2 transition-all duration-250 border-primary/50 hover:border-primary/80 focus:border-primary/80 outline-none bg-base-300"
              ></input>
            </fieldset>
            <fieldset className="flex flex-col">
              <label className="h-8 text-accent-content/90">- Password</label>
              <input
                ref={passwordRef}
                type="password"
                className="border-2 h-10 p-2 transition-all duration-250 border-primary/50 hover:border-primary/80 focus:border-primary/80 outline-none bg-base-300"
              ></input>
            </fieldset>

            {/* Error if any from the server */}
            <p className="text-error">{errorMsg}</p>

            <div className="p-2 flex justify-end">
              <button
                className={sMerge(
                  "shrink-0 transition-colors duration-200 font-bold px-4 py-2 rounded-md border-2 hover:brightness-90 border-accent active:brightness-80",
                  buttonColor
                )}
                onClick={handleLogin}
              >
                Login
              </button>
            </div>
          </Tabs.Content>

          {/* Register Form */}
          <Tabs.Content
            value="register"
            className="grow p-5 flex flex-col gap-2 h-fit"
          >
            <fieldset className="flex flex-col">
              <label className="h-8 text-accent-content/90">- Username</label>
              <input
                ref={usernameRef}
                className="border-2 h-10 p-2 transition-all duration-250 border-primary/50 hover:border-primary/80 focus:border-primary/80 outline-none bg-base-300"
              ></input>
            </fieldset>
            <fieldset className="flex flex-col">
              <label className="h-8 text-accent-content/90">- Password</label>
              <input
                ref={passwordRef}
                type="password"
                className="border-2 h-10 p-2 transition-all duration-250 border-primary/50 hover:border-primary/80 focus:border-primary/80 outline-none bg-base-300"
              ></input>
            </fieldset>
            <fieldset className="flex flex-col">
              <label className="h-8 text-accent-content/90">- Fullname</label>
              <input
                ref={fullnameRef}
                className="border-2 h-10 p-2 transition-all duration-250 border-primary/50 hover:border-primary/80 focus:border-primary/80 outline-none bg-base-300"
              ></input>
            </fieldset>

            {/* Error if any from the server */}
            <p className="text-error">{errorMsg}</p>

            <div className="p-2 flex justify-end">
              <button
                className={sMerge(
                  "shrink-0 transition-colors duration-200 font-bold px-4 py-2 rounded-md border-2 hover:brightness-90 border-accent active:brightness-80",
                  buttonColor
                )}
                onClick={handleRegister}
              >
                Register
              </button>
            </div>
          </Tabs.Content>
        </Tabs.Root>
      </div>
    </div>
  );
}
