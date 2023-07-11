// Based on: https://wwwtyro.net/2019/11/18/instanced-lines.html
#version 330

layout (location = 0) in vec2 a_p0;
layout (location = 1) in vec2 a_p1;
layout (location = 2) in vec2 a_vertex;
uniform mat4 u_mvp;
uniform vec2 u_resolution;
uniform float u_width;
uniform float u_z;

void main()
{
    // Convert from geometry coordinates to clip coordinates == NDC since this
    // is an orthographic projection.
    vec2 p0 = (u_mvp * vec4(a_p0, 0, 1)).xy;
    vec2 p1 = (u_mvp * vec4(a_p1, 0, 1)).xy;

    // Get a normal vector of the appropriate length for the screen resolution.
    // The constant K converts NDC coordinates to screen coordinates - the 0.5
    // factor is because the NDC cube is 2 units wide.  So, we first convert
    // the line to screen coordinates, scale its normal to a length of u_width,
    // then select if it is pointing "up" or "down" using a_vertex.y and
    // finally convert back to NDC by dividing.
    vec2 v_K     = 0.5 * u_resolution;
    vec2 v_line  = (p1 - p0) * v_K;
    vec2 nv_line = normalize(vec2(-v_line.y, v_line.x));
    vec2 nv      = nv_line * u_width * a_vertex.y / v_K;

    // The origin point for this vertex is either p0 or p1 depending on if we
    // are on the "left" or "right" side of the geometry, which is encoded in
    // a_vertex.x as 0 or 1.  We could also use a mixing function of some sort
    // which is how the original example did it deep in the math.
    p0 = (a_vertex.x == 0 ? p0 : p1);

    // Construct the final vector.
    gl_Position = vec4(p0 + nv, u_z, 1);
}
