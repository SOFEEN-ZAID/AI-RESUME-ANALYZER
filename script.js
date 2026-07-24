const TEXT_API_URL = "http://127.0.0.1:8000/analyze-text";
const FILE_API_URL = "http://127.0.0.1:8000/analyze-file";

const resumeText = document.getElementById("resumeText");
const resumeFile = document.getElementById("resumeFile");
const jobText = document.getElementById("jobText");
const analyzeBtn = document.getElementById("analyzeBtn");
const errorBox = document.getElementById("error");

const overallScore = document.getElementById("overallScore");
const similarityScore = document.getElementById("similarityScore");
const skillScore = document.getElementById("skillScore");
const keywordScore = document.getElementById("keywordScore");
const atsScore = document.getElementById("atsScore");
const matchedSkills = document.getElementById("matchedSkills");
const missingSkills = document.getElementById("missingSkills");
const missingKeywords = document.getElementById("missingKeywords");
const rolePredictions = document.getElementById("rolePredictions");
const categoryBreakdown = document.getElementById("categoryBreakdown");
const sectionReport = document.getElementById("sectionReport");
const suggestions = document.getElementById("suggestions");
const bullets = document.getElementById("bullets");
const recommendedProjects = document.getElementById("recommendedProjects");

function renderChips(container, items) {
  container.innerHTML = "";

  if (!items.length) {
    container.innerHTML = '<span class="chip">None found</span>';
    return;
  }

  items.forEach((item) => {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.textContent = item;
    container.appendChild(chip);
  });
}

function renderList(container, items) {
  container.innerHTML = "";
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    container.appendChild(li);
  });
}

function renderRoles(items) {
  rolePredictions.innerHTML = "";
  items.slice(0, 4).forEach((item) => {
    const card = document.createElement("div");
    card.className = "role-card";
    card.innerHTML = `
      <div>
        <strong>${item.role}</strong>
        <span>${item.score}% fit</span>
      </div>
      <div class="bar"><i style="width: ${item.score}%"></i></div>
      <small>Next skills: ${item.next_skills.join(", ") || "Keep strengthening project impact"}</small>
    `;
    rolePredictions.appendChild(card);
  });
}

function renderCategories(items) {
  categoryBreakdown.innerHTML = "";
  Object.entries(items).forEach(([name, detail]) => {
    const row = document.createElement("div");
    row.className = "breakdown-row";
    row.innerHTML = `
      <div>
        <strong>${name}</strong>
        <span>${detail.matched.length}/${detail.required.length || 0} matched</span>
      </div>
      <div class="bar"><i style="width: ${detail.score}%"></i></div>
    `;
    categoryBreakdown.appendChild(row);
  });
}

function renderSections(items) {
  sectionReport.innerHTML = "";
  Object.entries(items).forEach(([name, passed]) => {
    const item = document.createElement("span");
    item.className = passed ? "check pass" : "check fail";
    item.textContent = `${passed ? "OK" : "Fix"} ${name}`;
    sectionReport.appendChild(item);
  });
}

function renderProjects(items) {
  recommendedProjects.innerHTML = "";
  items.forEach((item) => {
    const card = document.createElement("article");
    card.className = "project-card";
    card.innerHTML = `
      <h3>${item.title}</h3>
      <p>${item.why}</p>
      <div class="chips">${item.skills_to_show.map((skill) => `<span class="chip">${skill}</span>`).join("")}</div>
    `;
    recommendedProjects.appendChild(card);
  });
}

function setLoading(isLoading) {
  analyzeBtn.disabled = isLoading;
  analyzeBtn.textContent = isLoading ? "Analyzing..." : "Analyze Match";
}

analyzeBtn.addEventListener("click", async () => {
  errorBox.textContent = "";

  if ((!resumeText.value.trim() && !resumeFile.files.length) || !jobText.value.trim()) {
    errorBox.textContent = "Please paste or upload a resume and add the job description.";
    return;
  }

  setLoading(true);

  try {
    let response;

    if (resumeFile.files.length) {
      const formData = new FormData();
      formData.append("resume", resumeFile.files[0]);
      formData.append("job_description", jobText.value);
      response = await fetch(FILE_API_URL, {
        method: "POST",
        body: formData,
      });
    } else {
      response = await fetch(TEXT_API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          resume_text: resumeText.value,
          job_description: jobText.value,
        }),
      });
    }

    if (!response.ok) {
      throw new Error("The analyzer API returned an error.");
    }

    const data = await response.json();

    overallScore.textContent = `${data.overall_score}%`;
    similarityScore.textContent = `${data.similarity_score}%`;
    skillScore.textContent = `${data.skill_score}%`;
    keywordScore.textContent = `${data.keyword_score}%`;
    atsScore.textContent = `${data.ats_score}%`;

    renderChips(matchedSkills, data.matched_skills);
    renderChips(missingSkills, data.missing_skills);
    renderChips(missingKeywords, data.missing_keywords);
    renderRoles(data.role_predictions);
    renderCategories(data.category_breakdown);
    renderSections(data.section_report);
    renderList(suggestions, data.suggestions);
    renderList(bullets, data.improved_resume_bullets);
    renderProjects(data.recommended_projects);
  } catch (error) {
    errorBox.textContent = "Could not connect to the API. Start the backend server first.";
  } finally {
    setLoading(false);
  }
});
