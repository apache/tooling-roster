# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""The admin data browser shows only what it is told to: the roster is the Secretary's."""

from __future__ import annotations

from typing import Any

from app.admin.routes import BROWSABLE, NOT_BROWSABLE
from app.db.models import DBBase


def test_every_table_is_either_browsable_or_kept_out_and_never_both() -> None:
    """A new model fails this until somebody decides whether an admin may see its rows, and which
    columns: read from the metadata, the browser would have shown a submission's address."""
    tables = {table.name: table for table in DBBase.metadata.sorted_tables}

    assert set(tables) - set(BROWSABLE) - NOT_BROWSABLE == set(), "decide these in app/admin/routes.py"
    assert set(BROWSABLE) & NOT_BROWSABLE == set()
    for name, columns in BROWSABLE.items():
        assert name in tables, f"{name} is no table"
        assert set(columns) <= {column.name for column in tables[name].columns}, f"{name} lists no such column"


async def test_a_table_that_is_in_the_database_but_not_listed_is_not_browsable(authenticated_client) -> None:
    """The browser is opt-in: a table that nobody listed is not read from the metadata, however personal its
    columns are. A throwaway table, in the database with a row, stands in for the next model somebody adds:
    a browser that read the metadata would show it, rather than fail on a table that is not there."""
    import sqlalchemy

    from app import db

    admin = await authenticated_client("zed", roles="admin")
    table = sqlalchemy.Table(
        "zz_people",
        DBBase.metadata,
        sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column("fullname", sqlalchemy.String),
    )
    try:
        async with db.session() as session:
            await session.run_sync(lambda sync: table.create(sync.get_bind()))
            await session.execute(table.insert().values(id=7, fullname="Grace Example"))
            await session.commit()
        response = await admin.get("/admin/data/zz_people")
    finally:
        DBBase.metadata.remove(table)

    text = await response.get_data(as_text=True)
    assert response.status_code == 404
    assert "fullname" not in text
    assert "Grace Example" not in text


async def test_a_table_not_listed_is_not_there(authenticated_client) -> None:
    admin = await authenticated_client("zed", roles="admin")

    assert (await admin.get("/admin/data/anything")).status_code == 404


async def test_a_listed_table_shows_only_the_columns_it_lists(authenticated_client, monkeypatch) -> None:
    """A column `BROWSABLE` does not name is neither selected nor shown, whatever it holds."""
    import sqlalchemy

    from app import db
    from app.admin import routes

    admin = await authenticated_client("zed", roles="admin")
    table = sqlalchemy.Table(
        "zz_people",
        DBBase.metadata,
        sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column("fullname", sqlalchemy.String),
    )
    monkeypatch.setitem(routes.BROWSABLE, "zz_people", ("id",))
    rendered: dict[str, Any] = {}
    real_render = routes.quart.render_template

    async def render(template: str, **context: Any) -> str:
        rendered.update(context)
        return await real_render(template, **context)

    monkeypatch.setattr(routes.quart, "render_template", render)
    try:
        async with db.session() as session:
            await session.run_sync(lambda sync: table.create(sync.get_bind()))
            await session.execute(table.insert().values(id=7, fullname="Grace Example"))
            await session.commit()
        response = await admin.get("/admin/data/zz_people")
    finally:
        DBBase.metadata.remove(table)

    text = await response.get_data(as_text=True)
    assert response.status_code == 200
    assert "fullname" not in text
    assert "Grace Example" not in text
    assert ">7<" in text
    # not only left out of the page: never selected, so never in what the template is handed
    assert rendered["columns"] == ["id"]
    assert [list(record) for record in rendered["records"]] == [["id"]]
