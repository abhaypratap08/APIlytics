// Resolves the project_id used by every read call.
//
// Priority:
//   1. ?project_id= URL query param (for demos with a specific project)
//   2. /api/v1/dev/context demo project (DEV_MODE only)
//
// Returns null while loading and if the backend is unreachable.

import { useEffect, useState } from "react";
import { api } from "../api/client";

export function useProject() {
  const [projectId, setProjectId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fromUrl = new URLSearchParams(window.location.search).get(
      "project_id",
    );
    if (fromUrl) {
      setProjectId(fromUrl);
      return;
    }

    let cancelled = false;
    api
      .devContext()
      .then((ctx) => {
        if (!cancelled) setProjectId(ctx.project_id);
      })
      .catch((e: Error) => {
        if (!cancelled) setError(e.message);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return { projectId, error };
}
