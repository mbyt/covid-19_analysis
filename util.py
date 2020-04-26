from datetime import datetime
import numpy as np
import scipy.optimize as op


MPL_FIG_TITLE_DATE_FORMAT = '%b%d'
MPL_FIG_SIZE_LARGE =(12.1, 8)
PD_FIG_SIZE_LARGE = (15, 8)
PD_FIG_SIZE_SMALL = (10, 4)
UNIX_DATE_DELTA = datetime(1970, 1, 1)
# numpy datetime64 timestamp is represented in nano seconds
DATETIME64_TO_DATETIME_SCALER = 1e-9


def isodate2xtick(date):
    return (date - UNIX_DATE_DELTA).days


def markdown_table_fmt(params):
    f = lambda x: ("%.4g" % x if isinstance(x, float) else
                   x.isoformat()[:10] if isinstance(x, datetime) else
                   x)
    s = (f(p) for p in params)
    return "| " + " | ".join(s) + " |"


def plot_pow2_fit(df, begin_date, end_date, expfct, key,
                  ndays=None, legend=False, figsize=PD_FIG_SIZE_SMALL, linestyle='o--',
                  date_to_xtick_fct=isodate2xtick):
    """
    param date_to_xtick_fct: one of {mdates.date2num, isodate2xtick}
    """
    # plot the dateframe
    mask = (begin_date <= df.index) & (df.index <= end_date)
    ax = df.loc[mask, key].plot(style='o-', figsize=figsize, legend=False)
    # calculate ndays
    _ylim = ax.get_ylim()
    x1 = date_to_xtick_fct(begin_date)
    if ndays is None:
        _x1, x2 = ax.get_xlim()
        assert abs(_x1 - x1) < 0.5, (
            'begin date repr differs: _x1 = %d, x1 = %d \n'
            'choose the other date_to_xtick_fct = {mdates.date2num, isodate2xtick}' % (_x1, x1)
        )
        arange_n = np.arange(int(x2 - x1 + 1))
    else:
        arange_n = np.arange(ndays)
    # plot the estimated exponentail function
    ax.plot(x1 + arange_n, expfct(arange_n), linestyle)
    ax.set_title("%s - %s" % ((begin_date.strftime(MPL_FIG_TITLE_DATE_FORMAT), end_date.strftime(MPL_FIG_TITLE_DATE_FORMAT))))
    ax.set_ylim(*_ylim)
    ax.set_xlim(x1, date_to_xtick_fct(end_date))
    ax.set_ylabel('total cases')
    return ax


def calc_pow2_zero(df, begin_date, rate, key):
    y0 = df.loc[begin_date == df.index, key][0]
    x0 = rate * np.log(y0) / np.log(2)
    return x0


L1 = lambda x: (abs(x)).mean()
L2 = lambda x: np.sqrt((x**2).mean())


def bfgs_curve_fit(f, xdata, ydata, p0, lagrange=1.0, norm=L2, bounds=None, verbose=True, tol=1e-13):
    """
    `bfgs_curve_fit` is my own `curve_fit` algorithm based on the
    "Limited memory Broyden-Fletcher-Goldfarb-Shannon with bound constraints"
    minimizer / optimizer. Corresponding links:
    * http://scipy.github.io/devdocs/generated/scipy.optimize.minimize.html#scipy.optimize.minimize
    * http://scipy.github.io/devdocs/optimize.minimize-lbfgsb.html
    * http://scipy.github.io/devdocs/generated/scipy.optimize.OptimizeResult.html#scipy.optimize.OptimizeResult
    """
    def bfgs_func(x, lagrange=1.0, norm=L2, ncols=2):
        ir = f(xdata, *x)
        ir = ir.reshape(-1, ncols)
        yrdata = ydata.reshape(-1, ncols)
        term = [norm(ir[:, nc] - yrdata[:, nc]) for nc in range(ncols)]
        assert ncols == 2
        return term[0] + lagrange * term[1]
    
    # previouse used values: ftol=1e-13, gtol=1e-13, eps=1e-7
    res = op.minimize(bfgs_func, p0, method='L-BFGS-B', args=(lagrange, norm),
                      bounds=bounds,
                      tol=tol, options=dict(disp=True))
    if verbose:
        print(res)
        min_val = bfgs_func(p0, lagrange=lagrange, norm=norm)
        print('  min_val:', min_val)
    return res['x'], res['hess_inv']