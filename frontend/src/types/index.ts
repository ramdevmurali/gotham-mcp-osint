export type ApiStatus = "success" | "error";

export type MissionResponse = {
  result: string;
  thread_id: string;
  status: ApiStatus;
};
