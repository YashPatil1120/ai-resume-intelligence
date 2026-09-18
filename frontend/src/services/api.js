const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function analyzeResume(resumeFile, jobDescription) {
  const formData = new FormData();

  /*
   * These names MUST match the FastAPI endpoint:
   *
   * resume_file: UploadFile = File(...)
   * job_description: str = Form(...)
   */

  formData.append("resume_file", resumeFile);
  formData.append("job_description", jobDescription);

  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    let errorMessage = "Failed to analyze resume.";

    try {
      const errorData = await response.json();

      if (errorData.detail) {
        errorMessage = errorData.detail;
      }
    } catch {
      // Keep the default error message
    }

    throw new Error(errorMessage);
  }

  return await response.json();
}