-- SQL-запросы проекта «Система управления релизами» (ПР7)

-- 1. Список продуктов (SELECT + ORDER BY)
SELECT id, name
FROM products
ORDER BY name;

-- 2. Релизы в окружении production (WHERE)
SELECT id, product_id, version, environment, status
FROM releases
WHERE environment = 'production'
ORDER BY release_date;

-- 3. Активные (не отменённые) релизы (WHERE)
SELECT id, product_id, version, release_date, status
FROM releases
WHERE status != 'cancelled'
ORDER BY release_date;

-- 4. Полная информация о релизе (JOIN)
SELECT
    r.id,
    r.version,
    r.environment,
    r.status,
    r.release_date,
    p.name AS product_name
FROM releases AS r
JOIN products AS p ON p.id = r.product_id
ORDER BY r.id;

-- 5. Продукты без активного релиза на выбранную дату (NOT IN)
SELECT p.id, p.name
FROM products AS p
WHERE p.id NOT IN (
    SELECT product_id
    FROM releases
    WHERE release_date = ?
      AND status != 'cancelled'
)
ORDER BY p.name;

-- 6. Количество активных релизов (агрегат)
SELECT COUNT(*) AS releases_count
FROM releases
WHERE status != 'cancelled';

-- 7. Количество релизов по продуктам (LEFT JOIN + GROUP BY)
SELECT
    p.id,
    p.name,
    COUNT(r.id) AS releases_count
FROM products AS p
LEFT JOIN releases AS r ON r.product_id = p.id
GROUP BY p.id, p.name
ORDER BY p.name;

-- 8. Продукты с числом релизов больше заданного (HAVING)
SELECT
    p.id,
    p.name,
    COUNT(r.id) AS releases_count
FROM products AS p
LEFT JOIN releases AS r ON r.product_id = p.id
GROUP BY p.id, p.name
HAVING COUNT(r.id) > ?
ORDER BY releases_count DESC;

-- 9. Список разработчиков
SELECT id, name, role
FROM developers
ORDER BY name;

-- 10. Задачи в статусе todo (WHERE)
SELECT id, title, developer_id, product_id, status
FROM tasks
WHERE status = 'todo'
ORDER BY id;

-- 11. Задачи с именами разработчика и продукта (JOIN)
SELECT
    t.id,
    t.title,
    t.status,
    d.name AS developer_name,
    p.name AS product_name
FROM tasks AS t
JOIN developers AS d ON d.id = t.developer_id
JOIN products AS p ON p.id = t.product_id
ORDER BY t.id;

-- 12. Релизы, готовые к публикации по упрощённому правилу
SELECT
    r.id,
    p.name AS product_name,
    r.version,
    r.environment,
    r.approvals_count,
    r.required_approvals
FROM releases AS r
JOIN products AS p ON p.id = r.product_id
WHERE r.status = 'planned'
  AND r.tests_passed = 1
  AND (
        r.environment = 'test'
     OR (r.environment = 'staging'
         AND (r.approvals_count >= 1 OR r.is_hotfix = 1))
     OR (r.environment = 'production'
         AND r.approvals_count >= r.required_approvals)
  )
ORDER BY r.release_date;
