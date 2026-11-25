/**
 * RoboSpine Trend Monitor — Google Workspace Bridge v2 (Newsletter HTML + Formatted Docs)
 *
 * 업데이트 방법 (기존 웹 앱 URL 그대로 유지!):
 * 1. https://script.google.com 의 기존 프로젝트에 이 코드를 덮어쓰기 후 Cmd+S 저장.
 * 2. 우측 상단 [배포] -> [배포 관리] -> 연필(수정) 아이콘 클릭
 * 3. 버전: [새 버전] 선택 -> [배포] 클릭 (URL은 바뀌지 않습니다!)
 */

const SHARED_SECRET = ""; // 선택: .env의 GWS_WEBHOOK_SECRET과 동일하게

const DOMAIN_LABELS = {
  harnesses: "로봇 하네스 · 아키텍처",
  embodied_models: "빅테크 · 연구 모델 실험",
  hardware_sdk: "로봇 플랫폼 · 미국/중국/한국/글로벌 깃헙 & SDK",
  ai_frontier: "프론티어 모델 · 에이전트 (20% 슬라이스)"
};

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    if (SHARED_SECRET && data.secret !== SHARED_SECRET) {
      return jsonOut({ ok: false, error: "unauthorized" });
    }

    const result = { ok: true, run_id: data.run_id };

    // 1. Google Docs: 마크다운 기호 없이 깔끔한 제목·볼드·링크 형식으로 최상단 추가
    if (data.doc_id && Array.isArray(data.events) && data.events.length > 0) {
      const doc = DocumentApp.openById(data.doc_id);
      const body = doc.getBody();
      let idx = 0;

      body.insertParagraph(idx++, "RoboSpine Trend Briefing · " + data.run_id)
          .setHeading(DocumentApp.ParagraphHeading.HEADING1);
      body.insertParagraph(idx++, "핵심 사건 " + data.events.length + "건 요약")
          .setForegroundColor("#475569");

      const domainOrder = ["harnesses", "embodied_models", "hardware_sdk", "ai_frontier"];
      domainOrder.forEach(function(dom) {
        const items = data.events.filter(function(ev) { return ev.domain === dom; });
        if (items.length === 0) return;

        body.insertParagraph(idx++, (DOMAIN_LABELS[dom] || dom) + " (" + items.length + "건)")
            .setHeading(DocumentApp.ParagraphHeading.HEADING2);

        items.forEach(function(ev) {
          const sig = Number(ev.significance || 0).toFixed(2);
          const tag = "[" + sig + "] [" + (ev.topic || "") + "] " + (ev.headline_ko || "");
          const pTitle = body.insertParagraph(idx++, tag);
          pTitle.setBold(true);
          if (ev.urls && ev.urls.length > 0) {
            pTitle.setLinkUrl(ev.urls[0]);
          }
          if (ev.detail_ko) {
            const pDesc = body.insertParagraph(idx++, "   " + ev.detail_ko);
            pDesc.setForegroundColor("#334155");
          }
        });
      });

      body.insertHorizontalRule(idx++);
      doc.saveAndClose();
      result.doc_updated = true;
    }

    // 2. Google Sheets: Events 탭에 신규 사건 행 추가
    if (data.sheet_id && Array.isArray(data.events) && data.events.length > 0) {
      const ss = SpreadsheetApp.openById(data.sheet_id);
      let sheet = ss.getSheetByName("Events") || ss.insertSheet("Events");
      if (sheet.getLastRow() === 0) {
        sheet.appendRow([
          "run_id", "occurred_at", "domain", "topic", "lab",
          "event_type", "significance", "official", "headline_ko", "detail_ko", "urls"
        ]);
      }
      data.events.forEach(function(ev) {
        sheet.appendRow([
          ev.run_id || data.run_id,
          ev.occurred_at || "",
          ev.domain || "",
          ev.topic || "",
          ev.lab || "",
          ev.event_type || "",
          ev.significance || 0,
          ev.official ? "TRUE" : "FALSE",
          ev.headline_ko || "",
          ev.detail_ko || "",
          (ev.urls || []).join(", ")
        ]);
      });
      result.sheet_rows_added = data.events.length;
    }

    // 3. Gmail: 리치 HTML 뉴스레터 본문 + HTML 파일 첨부 발송
    if (data.send_email && data.notify_email) {
      const subject = "[RoboSpine Trend] " + data.run_id + " 로봇 하네스 브리핑 (" + (data.events ? data.events.length : 0) + "건)";
      const plainFallback = data.markdown || "HTML 메일을 지원하는 클라이언트에서 확인해 주세요.";
      const options = {};
      if (data.html_email) {
        options.htmlBody = data.html_email;
        options.attachments = [
          Utilities.newBlob(data.html_email, "text/html", "robospine-trend-" + data.run_id + ".html")
        ];
      }
      GmailApp.sendEmail(data.notify_email, subject, plainFallback, options);
      result.email_sent = true;
    }

    return jsonOut(result);
  } catch (err) {
    return jsonOut({ ok: false, error: String(err) });
  }
}

function jsonOut(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
