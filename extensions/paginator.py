from dis_snek.models.discord_objects.components import (Button, InteractiveComponent)
from dis_snek.models.enums import ButtonStyles
from dis_snek.models.application_commands import component_callback


class FirstPageButton(Button):
    def __init__(self):
        super().__init__(style=ButtonStyles.PRIMARY, label="<<", custom_id="first")

    @component_callback(custom_id="first")
    async def callback(self, ctx, interaction: InteractiveComponent):
        assert self.view is not None
        embed = self.view.pages[0]
        view: PaginatorView = self.view
        self.view.currentpage = 1
        self.view.set_page(self.view.currentpage)
        await interaction.edit_message(embeds=[embed], components=Button(ButtonStyles.PRIMARY, "<<"))


class LastPageButton(Button):
    def __init__(self):
        super().__init__(style=ButtonStyles.PRIMARY, label=">>", custom_id="last")

    @component_callback(custom_id="last")
    async def callback(self, ctx, interaction: InteractiveComponent):
        assert self.view is not None
        embed = self.view.pages[self.view.last_page -1]
        self.view.currentpage = self.view.last_page
        self.view.set_page(self.view.currentpage)
        await interaction.edit_message(embeds=[embed], components=Button(ButtonStyles.PRIMARY, ">>"))


class NextPageButton(Button):
    def __init__(self):
        super().__init__(style=ButtonStyles.PRIMARY, label=">", custom_id="next")

    @component_callback(custom_id="next")
    async def callback(self, ctx, interaction: InteractiveComponent):
        assert self.view is not None
        view: PaginatorView = self.view

        if self.view.currentpage == self.view.last_page:
            embed = self.view.pages[0]
            self.view.currentpage = 1
        else:
            embed = self.view.pages[self.view.currentpage]
            self.view.currentpage += 1
        self.view.next_page()
        await interaction.edit_message(embeds=[embed], components=Button(ButtonStyles.PRIMARY, ">"))

class BackButton(Button):
    def __init__(self):
        super().__init__(style=ButtonStyles.PRIMARY, label="<", custom_id="back")

    @component_callback(custom_id="back")
    async def callback(self, ctx, interaction: InteractiveComponent):
        assert self.view is not None
        view: PaginatorView = self.view

        if self.view.currentpage == 1:
            embed = self.view.pages[self.view.last_page -1]
            self.view.currentpage = self.view.last_page
        else:
            embed = self.view.pages[self.view.currentpage -2]
            self.view.currentpage -= 1
        self.view.next_page()
        await interaction.edit_message(embeds=[embed], components=Button(ButtonStyles.PRIMARY, "<"))

class PageCounter(Button):
    def __init__(self, lastpage):
        super().__init__(
            label=f"Page 1/{lastpage}",
            style = ButtonStyles.GRAY,
            custom_id="page_counter",
            disabled=True
        )
    
    @component_callback(custom_id="page_counter")
    async def callback(self, interaction: InteractiveComponent):
        await interaction.defer()

class Cancel(Button):
    def __init__(self):
        super().__init__(style=ButtonStyles.DANGER, label="Cancel", custom_id="cancel")

    @component_callback(custom_id="cancel")
    async def callback(self, interaction: InteractiveComponent):
        