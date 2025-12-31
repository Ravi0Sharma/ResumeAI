import mammoth from "mammoth";
import * as pdfjsLib from "pdfjs-dist/legacy/build/pdf";
// Vite will bundle the worker and give us a URL string
import pdfWorkerUrl from "pdfjs-dist/legacy/build/pdf.worker.min.mjs?url";

pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorkerUrl;

export async function extractResumeText(file: File): Promise<string> {
  const ext = (file.name.split(".").pop() || "").toLowerCase();

  if (ext === "docx") {
    const arrayBuffer = await file.arrayBuffer();
    const result = await mammoth.extractRawText({ arrayBuffer });
    return (result.value || "").trim();
  }

  if (ext === "pdf") {
    const arrayBuffer = await file.arrayBuffer();
    const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    let fullText = "";
    for (let pageNum = 1; pageNum <= pdf.numPages; pageNum += 1) {
      const page = await pdf.getPage(pageNum);
      const content = await page.getTextContent();
      const pageText = content.items
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        .map((it: any) => (typeof it?.str === "string" ? it.str : ""))
        .join(" ");
      fullText += pageText + "\n";
    }
    return fullText.trim();
  }

  throw new Error("Unsupported file type. Please upload a PDF or DOCX.");
}


