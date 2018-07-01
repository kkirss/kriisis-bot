import api from '../api';

const ADD_SHOPS = 'SHOPS/ADD_SHOPS';

const initialState = {};

export default function shopsReducer(state = initialState, action) {
  switch (action.type) {
    case ADD_SHOPS: {
      if (action.shops.length > 0) {
        const newState = { ...state };

        action.shops.forEach((shop) => {
          newState[shop.id] = shop;
        });
        return newState;
      }
      return state;
    }
    default:
      return state;
  }
}

const addShops = shops => ({
  type: ADD_SHOPS,
  shops,
});

export const fetchShops = (dispatch) => {
  api.shops.fetch(null, { page_size: 1000 })
    .then((result) => {
      dispatch(addShops(result.results));
    });
};
