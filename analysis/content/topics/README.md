# Topic clusters (analysis/content/topics)

Offline analysis of the text of all posts and comments in ~/1f916-archive (data/posts, data/comments). REPORT.md has the method and the numbers. Figures are in figures/ (SVG plus a CSV with the plotted data, same stem); figures.json lists title, description, source CSV and n for each.

## Rerun

Needs the venv at ~/1f916-archive/.work/venv (pandas, numpy, scikit-learn, matplotlib, scipy):

    python3 -m venv ~/1f916-archive/.work/venv
    ~/1f916-archive/.work/venv/bin/pip install pandas numpy scikit-learn matplotlib scipy
    sh run_all.sh

Large intermediates go to ~/1f916-archive/.work/content_topics (not part of the output). Runtime is about 40 minutes; scripts 02 and 03 take most of it.

| script | does |
|---|---|
| common.py | paths, loaders, model-family rules (same as analysis/community) |
| 01_prepare.py | loads posts and comments, builds clean modelling text, flags short messages; writes sampling_summary.csv |
| 02_vectorize_sweep.py | TF-IDF matrix; NMF sweep k = 12 to 30 (coherence, stability); writes k_selection.csv |
| 03_fit.py | final NMF at the chosen k, KMeans cross-check, posts-only and comments-only models, seed rerun |
| 04_topics.py | reads labels.csv; excludes moderation placeholders; series flag; writes topics.csv, topic_terms.csv |
| 05_examples.py | topic_examples.csv (8 per cluster) |
| 06_time.py | topic_daily_share.csv, topic_weekly_share.csv, cluster_growth.csv, terms_fastest_*.csv, terms_growth_all.csv |
| 07_who_reply.py | handle by cluster, model family by cluster, reply structure |
| 08_vocab.py | vocab_distinctive.csv, coined_terms_top40.csv |
| 09_figures.py | 14 figures, figures.json |
| 10_validation_sample.py | draws the 150-message validation sample |
| 11_validation_score.py | scores validation_judgements_by_uid.csv |
| 12_report.py | assembles REPORT.md from the CSVs |

## Manual inputs

- labels.csv: cluster labels, written by hand from the top terms and by reading examples after script 03. Re-enter them if the clusters change (cluster ids can change on a rerun on another library version).
- validation_judgements_by_uid.csv: yes / partial / no per validation message, entered by reading each message. If a rerun draws a different sample, the missing judgements must be entered again; script 11 stops on an unjudged message.

## Files

Cluster tables: topics.csv, topic_terms.csv, topic_examples.csv, series_skeletons.csv, placeholder_messages.csv. Model checks: k_selection.csv, stability_final_k.csv, kmeans_agreement.json, kmeans_agreement_by_topic.csv, separate_models.csv, separate_model_match_*.csv. Time: topic_daily_share.csv, topic_weekly_share.csv, cluster_growth.csv, terms_*.csv. Authors: handle_by_cluster_top60_*.csv, cluster_handle_concentration.csv, family_by_cluster_*.csv, family_handles.csv. Replies: reply_structure_by_cluster.csv. Vocabulary: vocab_distinctive.csv, coined_terms_top40.csv. Validation: validation_sample.csv, validation_judgements.csv, validation_judgements_by_uid.csv, validation_by_cluster.csv.

## Notes

- Example urls follow https://1f916.ai/api/post/<id> and https://1f916.ai/api/comment/<id>; nothing was fetched from the site.
- In clusters where one handle writes more than half the messages (4, 6, 8, 12, 17), 4 of the 8 examples come from the top handle and 4 from other handles.
- Excerpts were screened for emails, phone-like numbers, addresses, long hashes and capitalised words that could be personal names; the screen is a heuristic.
- Model-family columns use the label each author declared; nothing verifies them.
