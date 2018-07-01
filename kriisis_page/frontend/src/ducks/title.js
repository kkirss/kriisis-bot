const SET_TITLE = 'TITLE/SET_TITLE';

const initialState = 'Kriisis Page';

export default function titleReducer(state = initialState, action) {
  switch (action.type) {
    case SET_TITLE:
      return {
        ...state,
        title: action.title,
      };
    default:
      return state;
  }
}

const setTitle = title => ({ type: SET_TITLE, title });

export const createTitle = title => (dispatch) => {
  dispatch(setTitle(title));
};
