import uvicorn


def main():
    uvicorn.run(
        "rstore_example_api.app:app",
        host="0.0.0.0",
        port=3000,
        reload=True
    )


if __name__ == "__main__":
    main()
