# Issue tracker: GitHub

Задачи и спецификации находятся в GitHub Issues репозитория
vakasyanov81/priceformation. Использовать CLI `gh` из корня клона.

## Операции

- Создать: `gh issue create --title "..." --body-file <file>`.
- Прочитать с комментариями: `gh issue view <number> --comments`.
- Получить поля: `gh issue view <number> --json number,title,body,labels,comments`.
- Список: `gh issue list --state open --json number,title,body,labels,comments`.
  При необходимости добавить фильтр `--label`.
- Комментарий: `gh issue comment <number> --body-file <file>`.
- Метки: `gh issue edit <number> --add-label "..."` или `--remove-label "..."`.
- Закрыть: `gh issue close <number>`.

Многострочный текст передавать через файл с фактическими переводами строк.

«Опубликовать в трекере» означает создать GitHub issue.
«Получить соответствующую задачу» означает прочитать issue с комментариями.

## Pull requests as a triage surface

**PRs as a request surface: no.**

## Wayfinding

Карта — issue с меткой `wayfinder:map` и разделами
Notes / Decisions-so-far / Fog.

Дочерние задачи связывать с картой как GitHub sub-issues через `gh api`.
Если эта возможность недоступна, использовать список задач в теле карты
и строку `Part of #<map>` в дочерней задаче.

Типы задач: `wayfinder:research`, `wayfinder:prototype`,
`wayfinder:grilling`, `wayfinder:task`.

Блокировки записывать через native issue dependencies:
`gh api --method POST repos/vakasyanov81/priceformation/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`.
Идентификатор блокирующей задачи получать через
`gh api repos/vakasyanov81/priceformation/issues/<number> --jq .id`.
Использовать database id, а не номер issue или node_id.
Если зависимости недоступны, записывать `Blocked by: #<number>` в начале тела.

Следующая доступная задача — первая по порядку карты открытая дочерняя
задача без исполнителя и открытых блокировок.
Взять задачу: `gh issue edit <number> --add-assignee @me`.
При завершении оставить комментарий с результатом, закрыть задачу
и добавить краткий вывод со ссылкой в Decisions-so-far карты.
