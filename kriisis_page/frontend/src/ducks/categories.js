import api from '../api';

const ADD_CATEGORIES = 'CATEGORIES/ADD_CATEGORIES';

const initialState = {};

export default function categoriesReducer(state = initialState, action) {
  switch (action.type) {
    case ADD_CATEGORIES: {
      if (action.categories.length > 0) {
        const newState = { ...state };

        action.categories.forEach((category) => {
          newState[category.id] = category;
        });
        return newState;
      }
      return state;
    }
    default:
      return state;
  }
}

const addCategories = categories => ({
  type: ADD_CATEGORIES,
  categories,
});

export const fetchCategories = (dispatch) => {
  api.categories.fetch(null, { page_size: 1000 })
    .then((result) => {
      dispatch(addCategories(result.results));
    });
};
