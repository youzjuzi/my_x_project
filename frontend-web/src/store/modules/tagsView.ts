import { defineStore } from 'pinia';
import type { RouteRecord } from 'vue-router';

interface ITagsViewState {
  visitedViews: Array<RouteRecord>;
}

export default defineStore({
  id: 'tagsView',
  state: (): ITagsViewState => ({
    visitedViews: []
  }),
  getters: {},
  actions: {
    addView(view) {
      this.addVisitedView(view);
    },
    addVisitedView(view) {
      if (this.visitedViews.some(v => v.path === view.path)) return;
      this.visitedViews.push(
        Object.assign({}, view, {
          title: view.meta.title || 'no-name'
        })
      );
    },
    delView(view) {
      this.delVisitedView(view);
    },
    delVisitedView(view) {
      for (const [i, v] of this.visitedViews.entries()) {
        if (v.path === view.path) {
          this.visitedViews.splice(i, 1);
          break;
        }
      }
    },

    delOthersViews(view) {
      this.delOthersVisitedViews(view);
    },
    delOthersVisitedViews(view) {
      this.visitedViews = this.visitedViews.filter(v => {
        return v.meta.affix || v.path === view.path;
      });
    },

    delAllViews() {
      this.delAllVisitedViews();
    },
    delAllVisitedViews() {
      // keep affix tags
      const affixTags = this.visitedViews.filter(tag => tag.meta.affix);
      this.visitedViews = affixTags;
    },

    updateVisitedView(view) {
      for (let v of this.visitedViews) {
        if (v.path === view.path) {
          v = Object.assign(v, view);
          break;
        }
      }
    }
  }
});
