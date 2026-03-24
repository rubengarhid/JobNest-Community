import { useProjectName } from "@/hooks/useProjectName";

export default function Home() {
  const { data: name, isLoading, isError } = useProjectName();

  if (isLoading) return <main>Loading...</main>;
  if (isError) return <main>Error fetching project name</main>;

  return (
    <main>
      <h1>{name}</h1>
    </main>
  );
}
