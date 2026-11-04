import sync_origin_main as engine

if __name__ == "__main__":
    try:
        raise SystemExit(engine.main())
    except Exception as exc:
        engine.emit({"additional_context": f"personal-agent git sync: aborted ({type(exc).__name__})"})
        raise SystemExit(0)
