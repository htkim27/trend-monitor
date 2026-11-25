/**
 * RoboSpine Trend Monitor — Google Workspace Bridge (Apps Script Web App)
 *
 * 배포 방법 (1회, 2분 소요):
 * 1. https://script.google.com 에서 새 프로젝트 생성 후 이 코드를 붙여넣기.
 * 2. 상단 SECRET 값을 원하는 문자열로 바꾸거나 비워둠.
 * 3. [배포] -> [새 배포] -> 유형: [웹 앱] -> 실행 주체: [나], 액세스 권한: [모든 사용자] -> 배포.
 * 4. 발급된 Web App URL을 config/settings.yaml 의 google_workspace.apps_script_webhook_url 에 입력.
 *    (doc_id, sheet_id, notify_email 도 함께 입력하면 자동 연동됩니다.)
 */

const SHARED_SECRET = ""; // 선택: settings.yaml의 webhook_secret과 동일하게 설정

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    if (SHARED_SECRET && data.secret !== SHARED_SECRET) {
      return jsonOut({ ok: false, error: "unauthorized" });
    }

    const result = { ok: true, run_id: data.run_id };

    // 1. Google Docs 최상단에 최신 회차 리포트 추가 (모바일 Docs 앱에서 열람)
    if (data.doc_id && data.markdown) {
      const doc = DocumentApp.openById(data.doc_id);
      const body = doc.getBody();
      body.insertHorizontalRule(0);
      body.insertParagraph(0, data.markdown);
      body.insertParagraph(0, "=== RoboSpine Trend Monitor · " + data.run_id + " ===")
          .setHeading(DocumentApp.ParagraphHeading.HEADING2);
      doc.saveAndClose();
      result.doc_updated = true;
    }

    // 2. Google Sheets 에 신규 사건 원장 행 추가
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

    // 3. Gmail 일간/회차 요약 브리핑 발송 (옵션)
    if (data.send_email && data.notify_email && data.markdown) {
      GmailApp.sendEmail(
        data.notify_email,
        "[RoboSpine Trend] " + data.run_id + " 브리핑",
        data.markdown
      );
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
