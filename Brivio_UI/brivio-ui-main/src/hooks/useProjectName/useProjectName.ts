import { useQuery } from "@tanstack/react-query";

const fetchProjectName = async (): Promise<string> => {
  const url = process.env.NEXT_PUBLIC_API_URL!;
  const apiKey = process.env.NEXT_PUBLIC_API_KEY!;
  const response = await fetch(`${url}/name`, {
    headers: {
      "x-api-key": apiKey,
    },
  });
  if (!response.ok) {
    throw new Error("Network response was not ok");
  }
  const data = await response.json();
  return data.name;
};

export const useProjectName = () => {
  return useQuery({
    queryKey: ["project-name"],
    queryFn: fetchProjectName,
  });
};
