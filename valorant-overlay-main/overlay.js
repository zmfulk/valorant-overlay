let lastDataJSON = "";

async function updateOverlay() {
  try {
    const res = await fetch(`overlay_data.json?t=${new Date().getTime()}`);
    if (!res.ok) return;

    const rawText = await res.text();
    if (rawText === lastDataJSON) return; // Skip DOM manipulation if no change
    lastDataJSON = rawText;

    const data = JSON.parse(rawText);

    // Update Team 1
    const t1Name = document.getElementById("team1Name");
    if (t1Name) t1Name.textContent = data.team1_name || "TEAM 1";
    
    const t1Score = document.getElementById("team1Score");
    if (t1Score) t1Score.textContent = data.team1_score ?? "0";
    
    const t1Logo = document.getElementById("team1Logo");
    if (t1Logo) {
      if (data.team1_logo && data.team1_logo.trim() !== "") {
        t1Logo.src = data.team1_logo;
        t1Logo.style.display = "block";
      } else {
        t1Logo.style.display = "none";
      }
    }

    // Update Team 2
    const t2Name = document.getElementById("team2Name");
    if (t2Name) t2Name.textContent = data.team2_name || "TEAM 2";
    
    const t2Score = document.getElementById("team2Score");
    if (t2Score) t2Score.textContent = data.team2_score ?? "0";
    
    const t2Logo = document.getElementById("team2Logo");
    if (t2Logo) {
      if (data.team2_logo && data.team2_logo.trim() !== "") {
        t2Logo.src = data.team2_logo;
        t2Logo.style.display = "block";
      } else {
        t2Logo.style.display = "none";
      }
    }

    // Update Match Metadata
    const phaseEl = document.getElementById("matchPhase");
    if (phaseEl) phaseEl.textContent = data.match_phase || "";
    
    const metaEl = document.getElementById("matchMeta");
    if (metaEl) metaEl.textContent = data.match_meta || "";

    // Update Map Box
    const mapBox = document.getElementById("mapBox");
    if (mapBox) {
      mapBox.style.display = data.show_map !== false ? "flex" : "none";
      const mapEl = document.getElementById("mapName");
      if (mapEl) mapEl.textContent = data.current_map || "ASCENT";
    }

    // Update League Box
    const leagueBox = document.getElementById("leagueBox");
    if (leagueBox) {
      leagueBox.style.display = data.show_league ? "flex" : "none";
      
      const leagueName = document.getElementById("leagueName");
      if (leagueName) leagueName.textContent = data.league_name || "NACE";
      
      const leagueLogo = document.getElementById("leagueLogo");
      if (leagueLogo) {
        if (data.league_logo && data.league_logo.trim() !== "") {
          leagueLogo.src = data.league_logo;
          leagueLogo.style.display = "block";
          leagueLogo.setAttribute("data-league", data.league_name);
        } else {
          leagueLogo.style.display = "none";
          leagueLogo.removeAttribute("data-league");
        }
      }
    }

    // Update Team Logos Visibility
    const showTeamLogos = data.show_team_logos !== false; // Defaults to true
    
    const logoBg = document.getElementById("logoBg");
    if (logoBg) logoBg.style.display = showTeamLogos ? "block" : "none";
    
    const team1LogoDrop = document.getElementById("team1LogoDrop");
    if (team1LogoDrop) team1LogoDrop.style.display = showTeamLogos ? "flex" : "none";
    
    const team2LogoDrop = document.getElementById("team2LogoDrop");
    if (team2LogoDrop) team2LogoDrop.style.display = showTeamLogos ? "flex" : "none";

  } catch (err) {
    // Graceful silent fail if file is being written
    console.error("Overlay update error:", err); // Added this so errors show up in OBS debug
  }
}

// Poll state every 250ms
setInterval(updateOverlay, 250);
updateOverlay();