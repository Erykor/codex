use super::*;
use crate::history_cell::HistoryRenderMode;
use crate::test_support::PathBufExt;
use crate::test_support::test_path_buf;
use codex_app_server_protocol::CommandExecutionSource;
use codex_app_server_protocol::CommandExecutionStatus;

#[test]
fn paginated_command_fallback_is_only_visible_in_full_transcript() {
    let item = ThreadItem::CommandExecution {
        id: "command-1".to_string(),
        plugin_id: None,
        script_path: None,
        command: "tmux capture-pane -p -S -25".to_string(),
        cwd: test_path_buf("/tmp").abs().into(),
        process_id: None,
        source: CommandExecutionSource::UnifiedExecStartup,
        status: CommandExecutionStatus::Completed,
        command_actions: Vec::new(),
        aggregated_output: Some("VITE v7.3.6 ready\n\nLocal: http://localhost:7133/".to_string()),
        exit_code: Some(0),
        duration_ms: Some(12),
    };
    let cell = transcript_only_fallback_cell(&item)
        .expect("command should have a transcript-only fallback");
    let render = |lines: Vec<Line<'static>>| {
        lines
            .into_iter()
            .map(|line| line.to_string())
            .collect::<Vec<_>>()
    };
    let main_display = render(cell.display_lines(/*width*/ 80));
    let main_raw = render(cell.raw_lines());
    let full_transcript = render(cell.transcript_lines(/*width*/ 80));
    let main_rich_height = cell.desired_height_for_mode(/*width*/ 80, HistoryRenderMode::Rich);
    let main_raw_height = cell.desired_height_for_mode(/*width*/ 80, HistoryRenderMode::Raw);
    let full_transcript_height = cell.desired_transcript_height(/*width*/ 80);

    insta::assert_snapshot!(
        format!(
            "main display: {main_display:?}\nmain raw: {main_raw:?}\nmain rich height: {main_rich_height}\nmain raw height: {main_raw_height}\nfull transcript height: {full_transcript_height}\nfull transcript:\n{full_transcript:#?}"
        ),
        @r###"
    main display: []
    main raw: []
    main rich height: 0
    main raw height: 0
    full transcript height: 5
    full transcript:
    [
        "$ tmux capture-pane -p -S -25",
        "status: Completed · exit 0",
        "  VITE v7.3.6 ready",
        "  ",
        "  Local: http://localhost:7133/",
    ]
    "###
    );
}
