const createApiClient = request => ({
  register: () => request("POST", `/session`),
  joinChannel: (channelName, userName) => (
    request("POST", `/channel/${channelName}/user/${userName}`)
  ),
  sendMessage: () => {

  }
});

export {
  createApiClient
};
