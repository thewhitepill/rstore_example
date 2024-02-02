import React, { useRef, useState } from "react";

import LauncherPage from "./LauncherPage";
import { initialStateFactory } from "./state";

const App = ({ apiClient }) => {
  const ws = useRef(null);
  const [state, setState] = useState(initialStateFactory);

  const handleLaunch = async ({ channelName, userName }) => {
    await apiClient.register();
    await apiClient.joinChannel(channelName, userName);
  };

  if (!state.isRegistered) {
    return (
      <LauncherPage onLaunch={handleLaunch} />
    )
  } else {
    throw Error();
  }
};

export default App;
