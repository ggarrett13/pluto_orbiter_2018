import plotly
import plotly.graph_objs as go
import numpy as np
from poliastro.util import time_range
import astropy.units as u
from poliastro.plotting import OrbitPlotter, OrbitPlotter3D, OrbitPlotter2D
from poliastro.twobody import Orbit
# from trajectory_tool.mnag_mission_analysis.planetary_flyby import PlanetaryFlyby
from copy import copy
from astropy import time
from poliastro.bodies import Sun
from astropy.coordinates import solar_system_ephemeris, get_body_barycentric_posvel
plotly.tools.set_credentials_file(username='GeoffreyGarrett', api_key='NNv5qParz0xFWQt16nhS')


def polytime_2_datetime(_time):
    temp = copy(_time)
    temp.format = 'datetime'
    return temp.value


def trace_point(position):
    return [go.Scatter3d(
        x=[position[0]],
        y=[position[1]],
        z=[position[2]],
        mode='marker'
    )]


def trace_body(radius):
    return [go.Surface(
        x=radius * np.outer(np.cos(np.linspace(0, 2 * np.pi, 100)),
                               np.sin(np.linspace(0, np.pi, 100))),
        y=radius * np.outer(np.sin(np.linspace(0, 2 * np.pi, 100)),
                               np.sin(np.linspace(0, np.pi, 100))),
        z=radius * np.outer(np.ones(100), np.cos(np.linspace(0, np.pi, 100))),
        colorscale=[[0, 'rgb(0, 0, 0)'],
                    [1, 'rgb(50, 50, 50)']],
        showscale=False,
        hoverinfo='Sphere of Influence (SOI)'
        # showline=True
                    )]


def trace_soi(r_soi_magnitude, position=np.array([0,0,0]), equatorial_plane=True):
    data = []

    x = position[0] + r_soi_magnitude * np.outer(np.cos(np.linspace(0, 2 * np.pi, 100)),
                               np.sin(np.linspace(0, np.pi, 100)))
    y = position[1] + r_soi_magnitude * np.outer(np.sin(np.linspace(0, 2 * np.pi, 100)),
                               np.sin(np.linspace(0, np.pi, 100)))
    z = position[2] + r_soi_magnitude * np.outer(np.ones(100), np.cos(np.linspace(0, np.pi, 100)))

    proj_z = lambda x, y, z: z  # projection in the z-direction
    colorsurfz = proj_z(x, y, z)
    z_offset = position[2] * np.ones(z.shape)  #
    x_offset = np.min(x) * np.ones(z.shape)
    y_offset = np.min(y) * np.ones(z.shape)

    sphere = go.Surface(
        x=x,
        y=y,
        z=z,
        colorscale=[[0, 'rgb(180, 40, 40)'],
                    [1, 'rgb(180, 40, 40)']],
        showscale=False,
        opacity=0.2,
                    )
    data.append(sphere)

    if equatorial_plane:
        tracez = go.Surface(z=z_offset,
                            x=x,
                            y=y,
                            colorscale=[[0, 'rgb(180, 40, 40)'],
                                        [1, 'rgb(180, 40, 40)']],
                            showlegend=False,
                            showscale=False,
                            text='testing',
                            hoverinfo='text',
                            opacity=0.4
                            )
        data.append(tracez)
    return data


def plot_planetary_flyby(planetary_flyby, data_return=False):
    planetary_flyby = planetary_flyby[0]
    op = OrbitPlotter3D()
    data = []
    body = planetary_flyby.planetary_node.body
    op.set_attractor(body)
    ss_i = Orbit.from_classical(attractor=body,
                                a=planetary_flyby.refined_attributes.sma_i,
                                ecc=np.linalg.norm(planetary_flyby.refined_attributes.ecc_i) * u.one,
                                inc=planetary_flyby.refined_attributes.inc * u.rad,
                                raan=planetary_flyby.refined_attributes.raan * u.rad,
                                argp=planetary_flyby.refined_attributes.argp * u.rad,
                                nu=0 * u.rad,
                                epoch=time.Time(planetary_flyby.planetary_node.epoch_periapsis))

    ss_f = Orbit.from_classical(attractor=body,
                                a=planetary_flyby.refined_attributes.sma_f,
                                ecc=np.linalg.norm(planetary_flyby.refined_attributes.ecc_f) * u.one,
                                inc=planetary_flyby.refined_attributes.inc * u.rad,
                                raan=planetary_flyby.refined_attributes.raan * u.rad,
                                argp=planetary_flyby.refined_attributes.argp * u.rad,
                                nu=0 * u.rad,
                                epoch=time.Time(planetary_flyby.planetary_node.epoch_periapsis))

    epoch_entry_dt = time.Time(planetary_flyby.planetary_node.epoch_entry)
    epoch_exit_dt = time.Time(planetary_flyby.planetary_node.epoch_exit)
    epoch_rp_dt = time.Time(planetary_flyby.planetary_node.epoch_periapsis)

    # Time frame arrays for entry and exit.
    tv_ent = time_range(epoch_entry_dt, periods=100, spacing=None, end=epoch_rp_dt)

    tv_ent_f = time_range(epoch_rp_dt, periods=100, spacing=None,
                          end=epoch_rp_dt + (epoch_rp_dt - epoch_entry_dt))

    tv_ext = time_range(epoch_rp_dt, periods=100, spacing=None, end=epoch_exit_dt)

    op.plot_trajectory(ss_i.sample(tv_ent)[-1], label='Entry hyperbole')
    op.plot_trajectory(ss_f.sample(tv_ext)[-1], label='Exit hyperbole')

    ss_i_after = ss_i.sample(tv_ent_f)[-1].get_xyz()

    ss_i_after_trace = go.Scatter3d(
        x=ss_i_after[0].value,
        y=ss_i_after[1].value,
        z=ss_i_after[2].value,
        mode='lines',
        line=dict(
            color='#1f77b4',
            width=7,
            dash="dash"
        ),
        text='Entry hyperbole extended',
        projection=dict(
            x=dict(
                show=True,
            ))
    )

    data.append(ss_i_after_trace)
    data += trace_body(10 * body.R.to(u.km).value)
    data += trace_soi(planetary_flyby.planetary_node.soi_periapsis_magnitude.value)
    data = data + op._data
    data += trace_point(planetary_flyby.planetary_node.soi_entry_position_body_ecliptic.value)
    data += trace_point(planetary_flyby.planetary_node.soi_exit_position_body_ecliptic.value)

    if data_return:
        return data

    else:
        layout = go.Layout(title="<b>{}</b> Flyby<br>Periapsis Epoch: {}".format(body, planetary_flyby.planetary_node.epoch_periapsis), width=800, height=800)
        fig = go.Figure(data=data, layout=layout)
        plotly.plotly.iplot(fig)


def fly_by_data_heliocentric(planetary_flyby, r=None, v=None, next_epoch=None):
    planetary_flyby = planetary_flyby

    test = Orbit.from_vectors(planetary_flyby.planetary_node.body, r=r, v=v, epoch=time.Time(planetary_flyby.planetary_node.epoch_entry))

    test_out =  test.propagate(time.TimeDelta((next_epoch - planetary_flyby.planetary_node.epoch_entry).total_seconds()*u.s))
    test_rout = test_out.state.r
    test_vout = test_out.state.v

    body = planetary_flyby.planetary_node.body
    ss_i = Orbit.from_classical(attractor=body,
                                a=planetary_flyby.refined_attributes.sma_i,
                                ecc=np.linalg.norm(planetary_flyby.refined_attributes.ecc_i) * u.one,
                                inc=planetary_flyby.refined_attributes.inc * u.rad,
                                raan=planetary_flyby.refined_attributes.raan * u.rad,
                                argp=planetary_flyby.refined_attributes.argp * u.rad,
                                nu=0 * u.rad,
                                epoch=time.Time(planetary_flyby.planetary_node.epoch_periapsis))

    ss_f = Orbit.from_classical(attractor=body,
                                a=planetary_flyby.refined_attributes.sma_f,
                                ecc=np.linalg.norm(planetary_flyby.refined_attributes.ecc_f) * u.one,
                                inc=planetary_flyby.refined_attributes.inc * u.rad,
                                raan=planetary_flyby.refined_attributes.raan * u.rad,
                                argp=planetary_flyby.refined_attributes.argp * u.rad,
                                nu=0 * u.rad,
                                epoch=time.Time(planetary_flyby.planetary_node.epoch_periapsis))

    epoch_entry_dt = time.Time(planetary_flyby.planetary_node.epoch_entry)
    epoch_exit_dt = time.Time(planetary_flyby.planetary_node.epoch_exit)
    epoch_rp_dt = time.Time(planetary_flyby.planetary_node.epoch_periapsis)

    # Time frame arrays for entry and exit.
    tv_ent = time_range(epoch_entry_dt, periods=100, spacing=None, end=epoch_rp_dt)

    tv_ext = time_range(epoch_rp_dt, periods=100, spacing=None, end=epoch_exit_dt)

    test_tv = time_range(start=epoch_entry_dt, end=epoch_exit_dt, periods=100, spacing=None)

    entry_rr = ss_i.sample(tv_ent)[-1]
    exit_rr = ss_f.sample(tv_ext)[-1]

    all_rr = test.sample(test_tv)[-1]

    body_rr_entry, _ = get_body_barycentric_posvel(str(planetary_flyby).lower().split(' ')[0], tv_ent)
    body_rr_exit, _ = get_body_barycentric_posvel(str(planetary_flyby).lower().split(' ')[0], tv_ext)

    #
    body_rr_test, _ = get_body_barycentric_posvel(str(planetary_flyby).lower().split(' ')[0], test_tv)

    x_bi, y_bi, z_bi = zip(entry_rr.get_xyz())
    x_hi, y_hi, z_hi = zip(body_rr_entry.get_xyz())

    x_bf, y_bf, z_bf = zip(exit_rr.get_xyz())
    x_hf, y_hf, z_hf = zip(body_rr_exit.get_xyz())

    x_te1, y_te1, z_te1 = zip(all_rr.get_xyz())

    #
    x_te2, y_te2, z_te2 = zip(body_rr_test.get_xyz())

    xi = np.array(x_bi[0].value)+np.array(x_hi[0].value)
    yi = np.array(y_bi[0].value)+np.array(y_hi[0].value)
    zi = np.array(z_bi[0].value)+np.array(z_hi[0].value)

    xf = np.array(x_bf[0].value)+np.array(x_hf[0].value)
    yf = np.array(y_bf[0].value)+np.array(y_hf[0].value)
    zf = np.array(z_bf[0].value)+np.array(z_hf[0].value)

    xt = np.array(x_te1[0].value)+np.array(x_te2[0].value)
    yt = np.array(y_te1[0].value)+np.array(y_te2[0].value)
    zt = np.array(z_te1[0].value)+np.array(z_te2[0].value)

    ##
#####
    #
    #
    ss_next = Orbit.from_vectors(Sun, r=np.array([xt[-1],yt[-1], zt[-1]])*u.km,
                                 v=test_vout+planetary_flyby.planetary_node.v_planet_f, epoch=epoch_exit_dt)
    test_tv_next = time_range(start=epoch_exit_dt, end=time.Time(next_epoch), periods=100, spacing=None)
    x, y, z = zip(ss_next.sample(test_tv_next)[-1].get_xyz())

    ss_next_test = go.Scatter3d(
        x=x[0].value,
        y=y[0].value,
        z=z[0].value,
        mode='lines',
        line=dict(
            color='#1f77b4',
            width=4,
        ),
        text='Entry hyperbole extended',
        projection=dict(
            x=dict(
                show=True,
            ))
    )

    ss_i_after_trace = go.Scatter3d(
        x=np.array(list(xi) + list(xf)),
        y=np.array(list(yi) + list(yf)),
        z=np.array(list(zi) + list(zf)),
        mode='lines',
        line=dict(
            color='purple',
            width=4,
        ),
        name='Hyperbolic Trajectory',
        projection=dict(
            x=dict(
                show=True,
            ))
    )

    # ss_f_after_trace = go.Scatter3d(
    #     x=xf,
    #     y=yf,
    #     z=zf,
    #     mode='lines',
    #     line=dict(
    #         color='green',
    #         width=4,
    #     ),
    #     projection=dict(
    #         x=dict(
    #             show=True,
    #         ))
    # )

    ss_f_test = go.Scatter3d(
        x=xt,
        y=yt,
        z=zt,
        mode='lines',
        line=dict(
            color='#1f77b4',
            width=4,
        ),
        text='Entry hyperbole extended',
        projection=dict(
            x=dict(
                show=True,
            ))
    )

    return [ss_i_after_trace, ss_f_test, ss_next_test]


def plot_propagation(ipj):
    # ss0 = Orbit.from_vectors(ipj.planetary_departure)
    pn0 = ipj.planetary_departure.planetary_node
    pn1 = ipj.planetary_flyby[0].planetary_node
    pn2 = ipj.planetary_rendezvous.planetary_node

    op = OrbitPlotter3D()

    op.set_attractor(Sun)

    # Departure body position at launch
    ss0 = Orbit.from_body_ephem(pn0.body, time.Time(pn0.epoch_exit, scale='tdb'))

    # Flyby body at entry to SOI
    ssl1 = Orbit.from_vectors(Sun, r=pn0.soi_exit_position_heliocentric, v=pn0.v_exit, epoch=time.Time(pn0.epoch_exit, scale='tdb'))

    #
    tv1 = time_range(start=pn0.epoch_exit, end=pn1.epoch_entry)

    op.plot(ss0, label=str(pn0.body)+' Departure')
    op.plot_trajectory(ssl1.sample(tv1)[-1], label='First Leg')

    ss1i = Orbit.from_body_ephem(pn1.body, time.Time(pn1.epoch_entry, scale='tdb'))
    ss1p = Orbit.from_body_ephem(pn1.body, time.Time(pn1.epoch_periapsis, scale='tdb'))
    ss1f = Orbit.from_body_ephem(pn1.body, time.Time(pn1.epoch_exit, scale='tdb'))

    ssl2 = Orbit.from_vectors(Sun, pn1.soi_exit_position_heliocentric, pn1.v_exit, time.Time(pn1.epoch_exit, scale='tdb'))

    tv2 = time_range(start=pn1.epoch_exit, end=pn2.epoch_entry)
    op._data += fly_by_data_heliocentric(ipj.planetary_flyby[0], r=pn1.soi_entry_position_body_ecliptic, v=(pn1.v_entry-pn1.v_planet_i), next_epoch=pn2.epoch_entry)
    op.plot(ss1p, label='{} Flyby'.format(str(pn1.body)))
    op.plot_trajectory(ssl2.sample(tv2)[-1], label='Second Leg')
    # op.plot(ss1i, label='{} SOI Entry'.format(str(pn1.body).split(' ')[0]), color=0.2)

    # op.plot(ss1f, label='{} SOI Exit'.format(str(pn1.body).split(' ')[0]), color=0.2)

    ss2 = Orbit.from_body_ephem(pn2.body, time.Time(pn2.epoch_entry, scale='tdb'))

    op.plot(ss2, label=str(pn2.body) + " Rendezvous")

    data = op._data
    # data += trace_soi(pn1.soi_periapsis_magnitude.value, ss1i.r.value, equatorial_plane=False)
    # data += trace_soi(pn1.soi_periapsis_magnitude.value, ss1f.r.value, equatorial_plane=False)
    data += trace_soi(pn1.soi_periapsis_magnitude.value, ss1p.r.value, equatorial_plane=False)
    # data += fly_by_data_heliocentric(ipj.planetary_flyby[0], r=pn1.soi_entry_position_body_ecliptic, v=(pn1.v_entry-pn1.v_planet_i), next_epoch=pn2.epoch_entry)

    layout = go.Layout(title="test", width=1000, height=800)
    fig = go.Figure(data=op._data, layout=layout)
    plotly.plotly.plot(fig)



