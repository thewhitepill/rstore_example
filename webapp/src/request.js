const createRequest = ({ baseUrl = "" }) => (
  async (method, url, data = null) => {
    const response = await fetch(
      `${baseUrl}${url}`,
      {
        method,
        credentials: "include",
        headers: {
          "Access-Control-Allow-Origin": "http://localhost:3000",
          "Content-Type": "application/json"
        },
        body: data ? JSON.stringify(data) : undefined
      }
    );

    return response.json();
  }
);

export {
  createRequest
};
